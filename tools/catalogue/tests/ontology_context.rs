use rare_omics_catalogue::{ontology_context, ontology_context_with_hgnc};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

const CROSSWALK: &str = include_str!("../../../research/registries/initial-disease-crosswalk.tsv");
const HGNC: &str = include_str!("../../../research/registries/hgnc-gene-references.json");

fn hash(bytes: &[u8]) -> String {
    Sha256::digest(bytes)
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect()
}

fn registry() -> Value {
    json!({"schema_version":1,"sources":[{
        "id":"UBERON","version":"synthetic-v1","url":"https://example.org/uberon.obo",
        "sha256":"a".repeat(64),"license":"synthetic fixture only","license_url":"https://example.org/terms"
    },{
        "id":"CL","version":"synthetic-v1","url":"https://example.org/cl.obo",
        "sha256":"b".repeat(64),"license":"synthetic fixture only","license_url":"https://example.org/terms"
    }],"mappings":[
        {"source_label":"tissue: Blood","source_id":"UBERON","term_id":"UBERON:0000178","term_label":"blood","predicate":"skos:exactMatch","evidence":"synthetic mapping test"},
        {"source_label":"cell type: Peripheral blood","source_id":"UBERON","term_id":"UBERON:0000178","term_label":"blood","predicate":"skos:broadMatch","evidence":"synthetic mapping test"},
        {"source_label":"tissue: whole blood","source_id":"UBERON","term_id":"UBERON:0000178","term_label":"blood","predicate":"skos:relatedMatch","evidence":"synthetic mapping test"},
        {"source_label":"cell type: ambiguous","source_id":"CL","term_id":"CL:0000057","term_label":"fibroblast","predicate":"skos:broadMatch","evidence":"synthetic ambiguity"},
        {"source_label":"cell type: ambiguous","source_id":"CL","term_id":"CL:0000540","term_label":"neuron","predicate":"skos:relatedMatch","evidence":"synthetic ambiguity"}
    ]})
}

fn assay(id: &str, labels: &[&str]) -> Value {
    json!({"dataset_accession":"GSE1","assay_accession":id,"organisms":["Homo sapiens"],
        "tissue_or_cell_annotations":labels,"private_patient_name":"do not copy",
        "diagnosis":"not an admitted diagnosis","participant_phenotypes":["HP:0000001"]})
}

fn encode(rows: &[Value]) -> Vec<u8> {
    rows.iter()
        .map(Value::to_string)
        .collect::<Vec<_>>()
        .join("\n")
        .into_bytes()
}

fn run(rows: &[Value], registry: &Value) -> Result<Value, String> {
    ontology_context(
        &encode(rows),
        CROSSWALK.as_bytes(),
        &serde_json::to_vec(registry).unwrap(),
    )
}

fn gene_registry() -> Value {
    serde_json::from_str(HGNC).unwrap()
}

fn run_hgnc(crosswalk: &str, genes: &Value) -> Result<Value, String> {
    ontology_context_with_hgnc(
        &encode(&[assay("GSM1", &["tissue: Blood"])]),
        crosswalk.as_bytes(),
        &serde_json::to_vec(&registry()).unwrap(),
        &serde_json::to_vec(genes).unwrap(),
    )
}

#[test]
fn hgnc_binding_preserves_source_assertions_and_existing_context() {
    let genes = gene_registry();
    let report = run_hgnc(CROSSWALK, &genes).unwrap();
    let records = report["reference_genes"].as_array().unwrap();
    assert_eq!(records.len(), 5);
    for (symbol, hgnc_id, entrez_id, ensembl_gene_id) in [
        ("KMT2D", "HGNC:7133", "8085", "ENSG00000167548"),
        ("KDM6A", "HGNC:12637", "7403", "ENSG00000147050"),
        ("NSD1", "HGNC:14234", "64324", "ENSG00000165671"),
        ("DNMT3A", "HGNC:2978", "1788", "ENSG00000119772"),
        ("EZH2", "HGNC:3527", "2146", "ENSG00000106462"),
    ] {
        let record = records.iter().find(|row| row["symbol"] == symbol).unwrap();
        assert_eq!(record["hgnc_id"], hgnc_id);
        assert_eq!(record["entrez_id"], entrez_id);
        assert_eq!(record["ensembl_gene_id"], ensembl_gene_id);
        assert_eq!(record["status"], "Approved");
        assert_eq!(record["in_withdrawn_source"], false);
    }
    let kmt2d = records.iter().find(|row| row["symbol"] == "KMT2D").unwrap();
    assert_eq!(kmt2d["prev_symbol"], json!(["MLL2", "TNRC21"]));
    assert_eq!(kmt2d["alias_symbol"], json!(["ALR", "CAGL114", "MLL4"]));
    assert_eq!(report["gene_reference_sources"], genes["sources"]);
    assert!(
        report["gene_reference_scope"]
            .as_str()
            .unwrap()
            .contains("HGNC assertions")
    );
    assert_eq!(
        report["input_sha256"]["hgnc_reference"],
        hash(&serde_json::to_vec(&genes).unwrap())
    );
    let mut original = report.clone();
    for key in [
        "gene_reference_scope",
        "gene_reference_sources",
        "reference_genes",
    ] {
        original.as_object_mut().unwrap().remove(key);
    }
    original["input_sha256"]
        .as_object_mut()
        .unwrap()
        .remove("hgnc_reference");
    assert_eq!(
        original,
        run(&[assay("GSM1", &["tissue: Blood"])], &registry()).unwrap()
    );
    assert_eq!(report["analysis_admitted"], false);
    assert_eq!(report["source_claims_verified"], false);
    assert!(report["independent_participant_count"].is_null());
    let mut reordered = genes.clone();
    reordered["sources"].as_array_mut().unwrap().reverse();
    reordered["records"].as_array_mut().unwrap().reverse();
    for record in reordered["records"].as_array_mut().unwrap() {
        record["alias_symbol"].as_array_mut().unwrap().reverse();
        record["prev_symbol"].as_array_mut().unwrap().reverse();
    }
    let reordered_report = run_hgnc(CROSSWALK, &reordered).unwrap();
    for key in [
        "reference_genes",
        "gene_reference_sources",
        "reference_diseases",
        "assays",
    ] {
        assert_eq!(report[key], reordered_report[key]);
    }
    assert_eq!(report, run_hgnc(CROSSWALK, &genes).unwrap());
}

#[test]
fn hgnc_declarations_reject_malformed_conflicting_and_withdrawn_records() {
    for (key, value) in [
        ("schema_version", json!(2)),
        ("sources", json!([])),
        ("records", json!([])),
        ("unexpected", json!(true)),
    ] {
        let mut genes = gene_registry();
        genes[key] = value;
        assert!(run_hgnc(CROSSWALK, &genes).is_err(), "{key}");
    }
    for (key, value) in [
        ("id", "Ensembl"),
        ("id", "HGNC-withdrawn"),
        ("version", ""),
        ("version", "another release"),
        ("license", ""),
        ("url", "http://example.org/hgnc.tsv"),
        ("license_url", "https://user@example.org/terms"),
        ("sha256", "invalid"),
    ] {
        let mut genes = gene_registry();
        genes["sources"][0][key] = json!(value);
        assert!(run_hgnc(CROSSWALK, &genes).is_err(), "{key}: {value}");
    }
    for (key, value) in [
        ("hgnc_id", json!("HGNC:invalid")),
        ("hgnc_id", json!("HGNC:07133")),
        ("symbol", json!("")),
        ("name", json!(" padded ")),
        ("status", json!("Entry Withdrawn")),
        ("in_withdrawn_source", json!(true)),
        ("in_withdrawn_source", json!("false")),
        ("entrez_id", json!("NCBIGene:8085")),
        ("entrez_id", json!("0")),
        ("ensembl_gene_id", json!("ENST00000167548")),
        ("ensembl_gene_id", json!("ENSG1")),
        ("alias_symbol", json!([""])),
        ("alias_symbol", json!(["ALR", "ALR"])),
        ("prev_symbol", json!(["MLL2", "MLL2"])),
        ("prev_symbol", json!("MLL2")),
        ("unknown", json!("not copied")),
    ] {
        let mut genes = gene_registry();
        genes["records"][0][key] = value;
        assert!(run_hgnc(CROSSWALK, &genes).is_err(), "{key}");
    }
    for key in ["hgnc_id", "symbol"] {
        let mut genes = gene_registry();
        genes["records"][1][key] = genes["records"][0][key].clone();
        assert!(run_hgnc(CROSSWALK, &genes).is_err(), "duplicate {key}");
    }
    let mut genes = gene_registry();
    let mut extra = genes["records"][0].clone();
    extra["hgnc_id"] = json!("HGNC:999999");
    extra["symbol"] = json!("EXTRA_SOURCE_GENE");
    genes["records"].as_array_mut().unwrap().push(extra);
    assert!(
        run_hgnc(CROSSWALK, &genes)
            .unwrap_err()
            .contains("not consumed")
    );
    let input = encode(&[assay("GSM1", &[])]);
    let mappings = serde_json::to_vec(&registry()).unwrap();
    let duplicate_key = HGNC.replace(
        "\"schema_version\":",
        "\"schema_version\":1,\"schema_version\":",
    );
    for bytes in [b"{".as_slice(), duplicate_key.as_bytes(), &[0xff]] {
        assert!(
            ontology_context_with_hgnc(&input, CROSSWALK.as_bytes(), &mappings, bytes).is_err()
        );
    }
    assert!(
        ontology_context_with_hgnc(b"invalid", CROSSWALK.as_bytes(), &mappings, HGNC.as_bytes())
            .is_err()
    );
}

#[test]
fn hgnc_joins_require_exact_current_id_and_symbol_without_alias_resolution() {
    let lines: Vec<_> = CROSSWALK.lines().collect();
    for (column, value, error) in [
        (1, "MLL4", "is an alias"),
        (1, "MLL2", "is a previous"),
        (1, "kmt2d", "approved symbol conflict"),
        (1, "KDM6A", "approved symbol conflict"),
        (2, "HGNC:12637", "approved symbol conflict"),
        (2, "HGNC:999999", "no selected source record"),
    ] {
        let mut row: Vec<_> = lines[1].split('\t').collect();
        row[column] = value;
        let crosswalk = format!("{}\n{}\n", lines[0], row.join("\t"));
        assert!(
            run_hgnc(&crosswalk, &gene_registry())
                .unwrap_err()
                .contains(error),
            "{column}: {value}"
        );
    }
    // An alias equal to another approved symbol is inert, not a competing join.
    let mut genes = gene_registry();
    genes["records"][0]["alias_symbol"]
        .as_array_mut()
        .unwrap()
        .push(json!("KDM6A"));
    let report = run_hgnc(CROSSWALK, &genes).unwrap();
    assert_eq!(report["reference_diseases"][0]["hgnc_id"], "HGNC:7133");
    // Distinct disease concepts may share the same exact gene reference.
    let mut row: Vec<_> = lines[1].split('\t').collect();
    row[3] = "MONDO:6666666";
    row[4] = "OMIM:666666";
    row[14] = "OMIM:666666";
    let crosswalk = format!("{CROSSWALK}{}\n", row.join("\t"));
    let report = run_hgnc(&crosswalk, &gene_registry()).unwrap();
    assert_eq!(report["reference_genes"].as_array().unwrap().len(), 5);
    assert_eq!(report["reference_diseases"].as_array().unwrap().len(), 6);
}

#[test]
fn source_context_preserves_mapping_direction_ambiguity_and_disease_scope() {
    let rows = [
        assay(
            "GSM2",
            &[
                "tissue: Blood",
                "cell type: Peripheral blood",
                "cell type: unknown",
                "cell type: ambiguous",
                "tissue: whole blood",
            ],
        ),
        assay("GSM1", &[]),
    ];
    let report = run(&rows, &registry()).unwrap();
    assert_eq!(
        report["summary"]["annotation_status_counts"],
        json!({"exact":1,"broader":1,"related":1,"ambiguous":1,"unmapped":1})
    );
    assert_eq!(report["summary"]["unreported_memberships"], 1);
    assert_eq!(report["assays"][0]["assay_accession"], "GSM1");
    assert_eq!(report["assays"][0]["context_status"], "unreported");
    let annotations = report["assays"][1]["annotations"].as_array().unwrap();
    let peripheral = annotations
        .iter()
        .find(|r| r["source_label"] == "cell type: Peripheral blood")
        .unwrap();
    assert_eq!(peripheral["candidates"][0]["source_id"], "UBERON");
    assert_eq!(peripheral["status"], "broader");
    let ambiguous = annotations
        .iter()
        .find(|r| r["status"] == "ambiguous")
        .unwrap();
    assert_eq!(ambiguous["candidates"].as_array().unwrap().len(), 2);
    assert_eq!(report["source_claims_verified"], false);
    assert_eq!(report["analysis_admitted"], false);
    assert!(report["independent_participant_count"].is_null());
    let diseases = report["reference_diseases"].as_array().unwrap();
    assert_eq!(diseases.len(), 5);
    let kabuki = diseases
        .iter()
        .find(|r| r["mondo_id"] == "MONDO:0007843")
        .unwrap();
    assert_eq!(kabuki["orpha_parent"], "ORPHA:2322");
    assert_eq!(kabuki["orpha_exact"], "");
    assert_eq!(kabuki["hpoa_unique_positive_terms"], 183);
    assert_eq!(kabuki["omim_mapping_evidence"], "MONDO:equivalentTo");
    assert_eq!(kabuki["hgnc_id"], "HGNC:7133");
    assert_eq!(
        kabuki["gene_relation"],
        "has_material_basis_in_germline_mutation_in"
    );
    for private in [
        "do not copy",
        "private_patient_name",
        "HP:0000001",
        "not an admitted diagnosis",
    ] {
        assert!(!report.to_string().contains(private));
    }
    assert_eq!(report["input_sha256"]["assays"], hash(&encode(&rows)));
    assert_eq!(
        report["input_sha256"]["disease_crosswalk"],
        hash(CROSSWALK.as_bytes())
    );
    assert_eq!(
        report["input_sha256"]["context_mappings"],
        hash(&serde_json::to_vec(&registry()).unwrap())
    );
    let mut reordered = registry();
    reordered["mappings"].as_array_mut().unwrap().reverse();
    reordered["sources"].as_array_mut().unwrap().reverse();
    let reordered_report = run(&[rows[1].clone(), rows[0].clone()], &reordered).unwrap();
    for key in ["assays", "reference_diseases", "sources", "summary"] {
        assert_eq!(report[key], reordered_report[key]);
    }
    assert_eq!(run(&rows, &registry()).unwrap(), report);
}

#[test]
fn invalid_reference_declarations_and_conflicting_mappings_fail_closed() {
    let rows = [assay("GSM1", &[])];
    for (key, value) in [
        ("schema_version", json!(2)),
        ("sources", json!([])),
        ("mappings", json!([])),
        ("unexpected", json!(true)),
        ("schema_version", json!("1")),
    ] {
        let mut reg = registry();
        reg[key] = value;
        assert!(run(&rows, &reg).is_err(), "{key}");
    }
    for (key, value) in [
        ("id", "GO"),
        ("version", ""),
        ("version", " padded "),
        ("license", "x\ny"),
        ("url", "not URL"),
        ("url", "http://example.org/x"),
        ("url", "https://user@example.org/x"),
        ("url", "https://:password@example.org/x"),
        ("sha256", "bad"),
        ("sha256", &"A".repeat(64)),
        ("license_url", "ftp://example.org/terms"),
    ] {
        let mut reg = registry();
        reg["sources"][0][key] = json!(value);
        assert!(run(&rows, &reg).is_err(), "{key}: {value}");
    }
    let mut reg = registry();
    let duplicate = reg["sources"][0].clone();
    reg["sources"].as_array_mut().unwrap().push(duplicate);
    assert!(run(&rows, &reg).is_err());
    for (key, value) in [
        ("source_id", "GO"),
        ("predicate", "owl:sameAs"),
        ("source_label", ""),
        ("term_id", "CL:0000178"),
        ("term_id", "UBERON:"),
        ("term_id", "UBERON:abc"),
        ("term_id", "UBERON:0178"),
        ("term_label", ""),
        ("evidence", ""),
    ] {
        let mut reg = registry();
        reg["mappings"][0][key] = json!(value);
        assert!(run(&rows, &reg).is_err(), "{key}: {value}");
    }
    for predicate in ["skos:exactMatch", "skos:broadMatch"] {
        let mut reg = registry();
        let mut duplicate = reg["mappings"][0].clone();
        duplicate["predicate"] = json!(predicate);
        reg["mappings"].as_array_mut().unwrap().push(duplicate);
        assert!(run(&rows, &reg).is_err());
    }
    let mut reg = registry();
    reg["mappings"][1]["term_label"] = json!("conflicting name");
    assert!(run(&rows, &reg).is_err());
    let bytes = serde_json::to_vec(&registry()).unwrap();
    let duplicate_field = String::from_utf8(bytes).unwrap().replace(
        "\"schema_version\":",
        "\"schema_version\":1,\"schema_version\":",
    );
    assert!(
        ontology_context(
            &encode(&rows),
            CROSSWALK.as_bytes(),
            duplicate_field.as_bytes()
        )
        .is_err()
    );
}

#[test]
fn invalid_disease_identity_and_hpoa_semantics_are_rejected() {
    let input = encode(&[assay("GSM1", &[])]);
    let mappings = serde_json::to_vec(&registry()).unwrap();
    let check = |bytes: &[u8]| ontology_context(&input, bytes, &mappings).is_err();
    for bytes in [b"".as_slice(), b"wrong header", &[0xff]] {
        assert!(check(bytes));
    }
    let lines: Vec<_> = CROSSWALK.lines().collect();
    assert!(check(lines[0].as_bytes()));
    assert!(check(format!("{}\nmissing columns\n", lines[0]).as_bytes()));
    for (field, value) in [
        (0, ""),
        (2, "HGNC:X"),
        (3, "MONDO:1"),
        (4, "OMIM:1"),
        (5, "related"),
        (6, "ORPHA:X"),
        (6, "ORPHA:2322"),
        (7, "bad"),
        (8, "related_to"),
        (10, "bad"),
        (11, "http://example.org"),
        (14, "OMIM:300867"),
        (15, "NaN"),
        (16, "187"),
        (17, "4"),
        (18, "unknown"),
    ] {
        let mut row: Vec<_> = lines[1].split('\t').collect();
        row[field] = value;
        assert!(
            check(format!("{}\n{}\n", lines[0], row.join("\t")).as_bytes()),
            "{field}: {value}"
        );
    }
    assert!(check(format!("{CROSSWALK}{}\n", lines[1]).as_bytes()));
    let mut row: Vec<_> = lines[2].split('\t').collect();
    row[4] = "OMIM:147920";
    row[14] = "OMIM:147920";
    assert!(check(
        format!("{}\n{}\n{}\n", lines[0], lines[1], row.join("\t")).as_bytes()
    ));
}

#[test]
fn catalogue_identity_and_unmapped_literals_are_explicit() {
    for (key, value) in [
        ("dataset_accession", json!("PXD1")),
        ("dataset_accession", json!("GSE")),
        ("assay_accession", json!("GSM")),
        ("assay_accession", json!("GSM1x")),
        ("organisms", json!([""])),
        ("tissue_or_cell_annotations", json!([""])),
        (
            "tissue_or_cell_annotations",
            json!(["tissue: Blood", "tissue: Blood"]),
        ),
    ] {
        let mut row = assay("GSM1", &[]);
        row[key] = value;
        assert!(run(&[row], &registry()).is_err(), "{key}");
    }
    assert!(run(&[assay("GSM1", &[]), assay("GSM1", &[])], &registry()).is_err());
    for bytes in [b"".as_slice(), b"{", &[0xff], b"\n", b"{}"] {
        assert!(
            ontology_context(
                bytes,
                CROSSWALK.as_bytes(),
                &serde_json::to_vec(&registry()).unwrap()
            )
            .is_err()
        );
    }
    let mut second_membership = assay("GSM1", &["tissue: blood"]);
    second_membership["dataset_accession"] = json!("GSE2");
    let report = run(&[assay("GSM1", &[]), second_membership], &registry()).unwrap();
    assert_eq!(report["summary"]["series_assay_memberships"], 2);
    assert_eq!(report["summary"]["annotation_status_counts"]["unmapped"], 1);
    assert!(report["independent_participant_count"].is_null());
}

#[test]
fn cli_validates_all_inputs_without_overwriting_them() {
    use std::{
        fs,
        path::Path,
        process::Command,
        time::{SystemTime, UNIX_EPOCH},
    };
    let root = std::env::temp_dir().join(format!(
        "ontology-context-{}-{}",
        std::process::id(),
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos()
    ));
    fs::create_dir_all(&root).unwrap();
    let assays = root.join("assays.jsonl");
    let diseases = root.join("diseases.tsv");
    let mappings = root.join("mappings.json");
    let hgnc = root.join("hgnc.json");
    let assay_bytes = encode(&[assay("GSM1", &["tissue: unknown"])]);
    fs::write(&assays, &assay_bytes).unwrap();
    fs::write(&diseases, CROSSWALK).unwrap();
    fs::write(&mappings, registry().to_string()).unwrap();
    fs::write(&hgnc, HGNC).unwrap();
    let call = |hgnc: Option<&Path>| {
        let mut command = Command::new(env!("CARGO_BIN_EXE_ontology-context"));
        command
            .arg("--assays")
            .arg(&assays)
            .arg("--diseases")
            .arg(&diseases)
            .arg("--mappings")
            .arg(&mappings);
        if let Some(path) = hgnc {
            command.arg("--hgnc").arg(path);
        }
        command.output().unwrap()
    };
    let output = call(None);
    assert!(output.status.success());
    let report: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(report["summary"]["annotation_status_counts"]["unmapped"], 1);
    assert!(report.get("reference_genes").is_none());
    assert_eq!(fs::read(&assays).unwrap(), assay_bytes);
    assert_eq!(fs::read_to_string(&diseases).unwrap(), CROSSWALK);
    assert_eq!(
        fs::read_to_string(&mappings).unwrap(),
        registry().to_string()
    );
    let output = call(Some(&hgnc));
    assert!(output.status.success());
    let enriched: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(enriched["reference_genes"].as_array().unwrap().len(), 5);
    assert_eq!(
        enriched["input_sha256"]["hgnc_reference"],
        hash(HGNC.as_bytes())
    );
    assert_eq!(enriched["assays"], report["assays"]);
    assert_eq!(fs::read_to_string(&hgnc).unwrap(), HGNC);
    fs::write(&hgnc, b"invalid").unwrap();
    let output = call(Some(&hgnc));
    assert_eq!(output.status.code(), Some(1));
    assert!(output.stdout.is_empty());
    assert_eq!(fs::read(&hgnc).unwrap(), b"invalid");
    fs::remove_file(&hgnc).unwrap();
    assert_eq!(call(Some(&hgnc)).status.code(), Some(1));
    for bytes in [b"invalid".to_vec(), vec![b' '; 16 * 1024 * 1024 + 1]] {
        fs::write(&mappings, &bytes).unwrap();
        let output = call(None);
        assert_eq!(output.status.code(), Some(1));
        assert!(output.stdout.is_empty());
        assert_eq!(fs::read(&mappings).unwrap(), bytes);
    }
    fs::remove_file(&assays).unwrap();
    let output = call(None);
    assert_eq!(output.status.code(), Some(1));
    fs::write(&assays, &assay_bytes).unwrap();
    fs::remove_file(&diseases).unwrap();
    let output = call(None);
    assert_eq!(output.status.code(), Some(1));
    fs::write(&diseases, CROSSWALK).unwrap();
    fs::remove_file(&mappings).unwrap();
    let output = call(None);
    assert_eq!(output.status.code(), Some(1));
    fs::remove_dir_all(root).unwrap();
}
