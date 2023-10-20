declare type TRunsRequestParams = {
    name: IProject['project_name'];
    repo_id?: string;
    run_name?: string;
    include_request_heads?: boolean;
};

declare type TDeleteRunsRequestParams = {
    name: IProject['project_name'];
    repo_id?: string;
    run_names: IRun['run_name'][];
};

declare type TStopRunsRequestParams = {
    name: IProject['project_name'];
    repo_id?: string;
    run_names: IRun['run_name'][];
    abort: boolean;
};


declare type TJobStatus =
    | 'pending'
    | 'submitted'
    | 'downloading'
    | 'running'
    | 'building'
    | 'uploading'
    | 'stopping'
    | 'stopped'
    | 'restarting'
    | 'terminating'
    | 'terminated'
    | 'aborting'
    | 'aborted'
    | 'failed'
    | 'done';

declare type TJobErrorCode =
    | "no_instance_matching_requirements"
    | "failed_to_start_due_to_no_capacity"
    | "interrupted_by_no_capacity"
    | "instance_terminated"
    | "container_exited_with_error"
    | "build_not_found"
    | "ports_binding_failed"


declare interface IRunJobHead {
    job_id: string,
    repo_ref: {
        repo_id: string,
    },
    hub_user_name: string,
    run_name: string,
    configuration_path: string,
    instance_type: string,
    workflow_name: null | string,
    provider_name: string,
    status: TJobStatus,
    error_code: null | TJobErrorCode,
    container_exit_code: number | null,
    submitted_at: number,
    artifact_paths: null | string[],
    tag_name: null | string,
    app_names: null | string[],
    instance_spot_type: string,
    price: number,
}

declare interface IRunAppHad {
    job_id: string
    artifact_path: string
}

declare interface IRunArtifactHad {
    job_id: string
    artifact_path: string
}

declare type TRepoInfo = 'none'

declare type RemoteRepoInfo = {
    repo_type: 'remote',
    "repo_host_name": string,
    "repo_port": number | null,
    "repo_user_name": string,
    "repo_name": string
}

declare type LocalRepoInfo = {
    repo_type: 'local',
    "repo_dir": string,
}

declare interface IRepoHead {
    repo_id: string,
    last_run_at: number,
    tags_count: number,
    repo_info: TRepoInfo | RemoteRepoInfo | LocalRepoInfo
}

declare interface IRequestHad {
    "job_id": string,
    "status": "fullfilled" | "provisioning" | "terminated" | "no_capacity",
    "message": string
}

declare interface IRunHead {
    run_name: string,
    workflow_name: string | null,
    provider_name: string | null,
    configuration_path: string,
    hub_user_name: string,
    artifact_heads: IRunArtifactHad[] | null,
    status: TJobStatus,
    submitted_at: number,
    tag_name: string | null,
    app_heads: IRunAppHad[] | null,
    request_heads: IRequestHad[] | null,
    job_heads: IRunJobHead[],
}

declare interface IRunListItem {
    project: string,
    repo_id: null | string,
    backend: TBackendType,
    repo: null | IRepoHead;
    run_head: IRunHead
}

declare interface IRun extends Omit<IRunHead, 'configuration_path'> {
    repo: IRepoHead,
    repo_user_id: string,
}

