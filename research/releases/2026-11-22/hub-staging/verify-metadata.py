#!/usr/bin/env python3
"""Read-only verification of the 13-object metadata subset; never closes raw publication."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import time

from huggingface_hub import HfApi
from huggingface_hub.hf_api import RepoFile


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[4])
    parser.add_argument('--hub-revision',required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    parser.add_argument('--include-staging-manifest',action='store_true')
    args=parser.parse_args()
    started=time.monotonic()
    receipt={'schema_version':1,'record_type':'metadata_subset_receipt','status':'verification_started',
        'publication_route':'hugging_face_browser_editor','automated_publisher_upload_executed':False,
        'official_github_actions_run_observed':False,'full_release_verified':False,
        'full_publication_track_status':'open_raw_transfer_blocked','raw_archives_published_by_this_route':0,
        'hub_revision':args.hub_revision,'checked_at':datetime.now(timezone.utc).isoformat(),
        'verification_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'python_version':sys.version}
    receipt_safe=False
    try:
        publisher_path=args.root/'tools/hf-release/publisher.py'
        # Reject lexical symlinks before loading the shared path-validation functions.
        if any(path.is_symlink() for path in [publisher_path,*publisher_path.parents]):
            raise ValueError('symlink in publisher path')
        if hashlib.sha256(publisher_path.read_bytes()).hexdigest()!='1641709238710f6496b3fed1d8983aa9fa3f867cc50cd68753df69a85a447aea':
            raise ValueError('publisher differs from the reviewed implementation')
        spec=importlib.util.spec_from_file_location('publisher',publisher_path);publisher=importlib.util.module_from_spec(spec);sys.modules[spec.name]=publisher;spec.loader.exec_module(publisher)
        receipt_path=publisher.local_path(args.receipt.absolute().parent,args.receipt.name)
        manifest_path=publisher.local_path(args.root,'research/releases/2026-11-22/hub-staging/staging-publication-manifest.json')
        full_manifest_path=publisher.local_path(args.root,'research/releases/2026-11-22/manifest.json')
        script_path=publisher.local_path(Path(__file__).absolute().parent,Path(__file__).name)
        protected={manifest_path.resolve(),full_manifest_path.resolve(),script_path.resolve()}
        protected.update(publisher.local_path(args.root,f'tools/hf-release/{name}').resolve() for name in ('publisher.py','pyproject.toml','uv.lock'))
        if receipt_path.resolve() in protected:raise ValueError('receipt would overwrite a verification input')
        manifest_bytes=manifest_path.read_bytes();manifest=json.loads(manifest_bytes)
        protected.update(publisher.local_path(args.root,obj['source_path']).resolve() for obj in manifest['objects'])
        if receipt_path.resolve() in protected:raise ValueError('receipt would overwrite a verification input')
        # No failure report may be written until every consumed input is protected.
        receipt_safe=True
        if not re.fullmatch(r'[0-9a-f]{40}',args.hub_revision):raise ValueError('full immutable Hub SHA required')
        if importlib.metadata.version('huggingface-hub')!='2.4.0':raise ValueError('reviewed Hub client 2.4.0 required')
        baseline=manifest['baseline_source_revision']
        if len(manifest['objects'])!=13 or manifest['full_release_status']!='pending_raw_archives':raise ValueError('unexpected metadata subset contract')
        full_bytes=full_manifest_path.read_bytes()
        if hashlib.sha256(full_bytes).hexdigest()!=manifest['planned_full_manifest_sha256']:raise ValueError('planned full release manifest changed')
        original_publisher=subprocess.check_output(['git','-C',str(args.root),'show',f'{baseline}:tools/hf-release/publisher.py'])
        if publisher_path.read_bytes()!=original_publisher:raise ValueError('read-back implementation differs from reviewed baseline')
        payloads=[];origins=[];seen=set()
        for obj in manifest['objects']:
            if obj['kind']!='metadata' or obj['path_in_repo'] in seen:raise ValueError('invalid or duplicate subset object')
            seen.add(obj['path_in_repo']);publisher.relative_path(obj['path_in_repo'])
            local=publisher.local_path(args.root,obj['source_path']);payload=publisher.verify_file(local,obj)
            origin=obj['origin']
            if origin['kind']=='unchanged_github_blob':
                if origin['revision']!=baseline:raise ValueError('baseline source revision mismatch')
                original=subprocess.check_output(['git','-C',str(args.root),'show',f"{baseline}:{origin['path']}"])
                if original!=local.read_bytes() or payload.git_blob_sha1!=origin['git_blob_sha1']:raise ValueError('metadata differs from its immutable Git origin')
            elif origin['kind']=='new_staging_notice':
                if origin.get('revision') is not None:raise ValueError('new notice must not claim an unverified baseline origin')
            else:raise ValueError('unknown notice/source origin')
            payloads.append(payload);origins.append(origin)
        if sum(o['kind']=='unchanged_github_blob' for o in origins)!=10 or sum(o['kind']=='new_staging_notice' for o in origins)!=3:raise ValueError('unexpected source-origin counts')
        if args.include_staging_manifest:
            payloads.append(publisher.bytes_payload('releases/2026-11-22/staging-publication-manifest.json',manifest_bytes))
        api=HfApi(token=False);info=api.repo_info(manifest['repo_id'],repo_type='dataset',revision=args.hub_revision)
        if info.private is not False or info.sha!=args.hub_revision:raise ValueError('public exact Hub revision not confirmed')
        receipt['remote_objects']=publisher.verify_remote(api,manifest['repo_id'],args.hub_revision,payloads)
        files=[item.path for item in api.list_repo_tree(manifest['repo_id'],repo_type='dataset',revision=args.hub_revision,recursive=True) if isinstance(item,RepoFile)]
        raw=[path for path in files if path.lower().endswith(('.tar','.idat','.idat.gz','.zip'))]
        receipt['raw_archive_paths_observed']=raw
        if raw:raise ValueError('raw object present; reconcile metadata-only notices before acceptance')
        receipt.update({'status':'metadata_subset_ui_published_api_verified_raw_pending','repo_id':manifest['repo_id'],
            'hub_commit_url':f"https://huggingface.co/datasets/{manifest['repo_id']}/commit/{args.hub_revision}",
            'baseline_source_revision':baseline,'staging_manifest_sha256':hashlib.sha256(manifest_bytes).hexdigest(),
            'verified_metadata_objects':13,'verified_additional_staging_manifest':args.include_staging_manifest,
            'unchanged_baseline_files':10,'new_notice_files':3,'raw_archive_absence_checked':True,
            'huggingface_hub_version':'2.4.0','publication_acceptance':'metadata subset only; full T09 remains open'})
        exit_code=0
    except Exception as exc:
        receipt['status']='verification_failed'
        receipt['failure']={'type':type(exc).__name__,'message':str(exc) if type(exc).__name__ in ('ValueError','ReleaseError') else 'read-only verification failed; arbitrary exception details withheld'}
        exit_code=1
    receipt['elapsed_seconds']=time.monotonic()-started
    if receipt_safe:publisher.write_receipt(receipt_path,receipt)
    print(json.dumps({'status':receipt['status'],'verified_remote_objects':len(receipt.get('remote_objects',[])),'full_release_verified':False}))
    return exit_code


if __name__=='__main__':raise SystemExit(main())
