use rare_omics_catalogue::ontology_context;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

const CROSSWALK: &str = include_str!("../../../research/registries/initial-disease-crosswalk.tsv");

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
    let assay_bytes = encode(&[assay("GSM1", &["tissue: unknown"])]);
    fs::write(&assays, &assay_bytes).unwrap();
    fs::write(&diseases, CROSSWALK).unwrap();
    fs::write(&mappings, registry().to_string()).unwrap();
    let call = || {
        Command::new(env!("CARGO_BIN_EXE_ontology-context"))
            .arg("--assays")
            .arg(&assays)
            .arg("--diseases")
            .arg(&diseases)
            .arg("--mappings")
            .arg(&mappings)
            .output()
            .unwrap()
    };
    let output = call();
    assert!(output.status.success());
    let report: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(report["summary"]["annotation_status_counts"]["unmapped"], 1);
    assert_eq!(fs::read(&assays).unwrap(), assay_bytes);
    assert_eq!(fs::read_to_string(&diseases).unwrap(), CROSSWALK);
    assert_eq!(
        fs::read_to_string(&mappings).unwrap(),
        registry().to_string()
    );
    for bytes in [b"invalid".to_vec(), vec![b' '; 16 * 1024 * 1024 + 1]] {
        fs::write(&mappings, &bytes).unwrap();
        let output = call();
        assert_eq!(output.status.code(), Some(1));
        assert!(output.stdout.is_empty());
        assert_eq!(fs::read(&mappings).unwrap(), bytes);
    }
    fs::remove_file(&assays).unwrap();
    let output = call();
    assert_eq!(output.status.code(), Some(1));
    fs::write(&assays, &assay_bytes).unwrap();
    fs::remove_file(&diseases).unwrap();
    let output = call();
    assert_eq!(output.status.code(), Some(1));
    fs::write(&diseases, CROSSWALK).unwrap();
    fs::remove_file(&mappings).unwrap();
    let output = call();
    assert_eq!(output.status.code(), Some(1));
    fs::remove_dir_all(root).unwrap();
}
