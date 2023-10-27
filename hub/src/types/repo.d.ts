enum RepoTypeEnum {
    REMOTE = 'remote',
    LOCAL = 'local',
}

declare interface ILocalRepoInfo {
    repo_dir: string,
    repo_type: RepoTypeEnum.LOCAL,
}

declare interface IRemoteRepoInfo {
    repo_host_name: string,
    repo_port: number | null,
    repo_user_name: string,
    repo_name: string
    repo_type: RepoTypeEnum.REMOTE,
}

declare interface IRepo {
    repo_id: string,
    repo_info : ILocalRepoInfo | IRemoteRepoInfo
}
