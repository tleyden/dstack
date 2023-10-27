
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
    project_role: TProjectRole,
    user: IUser
}

declare type TSetProjectMembersParams = {
    project_name: string,
    members: Array<{
        project_role: TProjectRole,
        username: string
    }>
}

declare type TProjectRole = TUserRole
