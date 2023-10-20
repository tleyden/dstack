declare type TUserRole = 'read' | 'admin' | 'run'

declare interface IUser {
    id: string,
    username: string;
    global_role: TUserRole
}

declare interface IUserWithCreds extends IUser {
    "creds": {
        "token": string
    }
}

declare interface IUserAuthData extends Pick<IUserWithCreds['creds'], 'token'>{}
