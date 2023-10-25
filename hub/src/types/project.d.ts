
declare type TProjectBackend = {
    name: string,
    config: IBackendAWS | IBackendAzure | IBackendGCP | IBackendLambda | IBackendLocal
}
declare interface IProject {
    project_name: string,
    members: IProjectMember[],
    backends: TProjectBackend[]
}

declare interface IProjectMember {
    user_name: string,
    project_role: TProjectRole,
}

declare type TProjectRole = 'read' | 'run' | 'admin'
