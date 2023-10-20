const BASE_URL = process.env.API_URL;

export const API = {
    BASE: () => `${BASE_URL}`,
    USERS: {
        BASE: () => `${API.BASE()}/users`,
        LIST: () => `${API.USERS.BASE()}/list`,
        CREATE: () => `${API.USERS.BASE()}/create`,
        UPDATE: () => `${API.USERS.BASE()}/update`,
        DETAILS: () => `${API.USERS.BASE()}/get_user`,
        CURRENT_USER: () => `${API.USERS.BASE()}/get_my_user`,
        REFRESH_TOKEN: () => `${API.USERS.BASE()}/refresh_token`,
    },

    PROJECTS: {
        BASE: () => `${API.BASE()}/projects`,
        LIST: () => `${API.PROJECTS.BASE()}/list`,
        CREATE: () => `${API.PROJECTS.BASE()}/create`,
        DELETE: () => `${API.PROJECTS.BASE()}/delete`,
        DETAILS: (name: IProject['project_name']) => `${API.PROJECTS.BASE()}/${name}`,
        DETAILS_INFO: (name: IProject['project_name']) => `${API.PROJECTS.DETAILS(name)}/get`,
        MEMBERS: (name: IProject['project_name']) => `${API.PROJECTS.DETAILS(name)}/set_members`,

        // Repos
        REPOS: (projectName: IProject['project_name']) => `${API.BASE()}/project/${projectName}/repos`,
        REPO_LIST: (projectName: IProject['project_name']) => `${API.PROJECTS.REPOS(projectName)}/list`,
        REPO_ITEM: (projectName: IProject['project_name']) => `${API.PROJECTS.REPOS(projectName)}/get`,
        DELETE_REPO: (projectName: IProject['project_name']) => `${API.PROJECTS.REPOS(projectName)}/delete`,
        UPLOAD_CODE: (projectName: IProject['project_name']) => `${API.PROJECTS.REPOS(projectName)}/upload_code`,

        // Runs
        RUNS: (projectName: IProject['project_name']) => `${API.BASE()}/project/${projectName}/runs`,
        RUNS_LIST: (projectName: IProject['project_name']) => `${API.PROJECTS.RUNS(projectName)}/list`,
        RUN_DETAILS: (projectName: IProject['project_name']) => `${API.PROJECTS.RUNS(projectName)}/get`,
        RUN_GET_PLAN: (projectName: IProject['project_name']) => `${API.PROJECTS.RUNS(projectName)}/get_plan`,
        RUNS_DELETE: (projectName: IProject['project_name']) => `${API.PROJECTS.RUNS(projectName)}/delete`,
        RUNS_STOP: (projectName: IProject['project_name']) => `${API.PROJECTS.RUNS(projectName)}/stop`,
        RUNS_SUBMIT: (projectName: IProject['project_name']) => `${API.PROJECTS.RUNS(projectName)}/submit`,

        // Logs
        LOGS: (projectName: IProject['project_name']) => `${API.BASE()}/project/${projectName}/logs/poll`,

        // Logs
        ARTIFACTS: (projectName: IProject['project_name']) => `${API.BASE()}/project/${projectName}/artifacts/list`,

        // Tags
        TAG_LIST: (projectName: IProject['project_name']) => `${API.BASE()}/project/${projectName}/tags/list/heads`,
        TAG_ITEM: (projectName: IProject['project_name'], tagName: ITag['tag_name']) =>
            `${API.BASE()}/project/${projectName}/tags/${tagName}`,

        // Secrets
        SECRET_LIST: (projectName: IProject['project_name']) => `${API.BASE()}/project/${projectName}/secrets/list`,
        SECRET_ADD: (projectName: IProject['project_name']) => `${API.BASE()}/project/${projectName}/secrets/add`,
        SECRET_UPDATE: (projectName: IProject['project_name']) => `${API.BASE()}/project/${projectName}/secrets/update`,
        SECRET_DELETE: (projectName: IProject['project_name'], secretName: ISecret['secret_name']) =>
            `${API.BASE()}/project/${projectName}/secrets/${secretName}/delete`,
    },

    BACKENDS: {
        BASE: () => `${API.BASE()}/backends`,
        LIST_TYPES: () => `${API.BACKENDS.BASE()}/list_types`,
        CONFIG_VALUES: () => `${API.BACKENDS.BASE()}/config_values`,
    },

    PROJECT_BACKENDS: {
        BASE: (projectName: IProject['project_name']) => `${API.BASE()}/project/${projectName}/backends`,
        LIST: (projectName: IProject['project_name']) => `${API.PROJECT_BACKENDS.BASE(projectName)}/list`,
        CREATE: (projectName: IProject['project_name']) => `${API.PROJECT_BACKENDS.BASE(projectName)}/create`,
        UPDATE: (projectName: IProject['project_name']) => `${API.PROJECT_BACKENDS.BASE(projectName)}/update`,
        DELETE: (projectName: IProject['project_name']) => `${API.PROJECT_BACKENDS.BASE(projectName)}/delete`,
        BACKEND_CONFIG_INFO: (projectName: IProject['project_name'], backendName: string) =>
            `${API.PROJECT_BACKENDS.BASE(projectName)}/${backendName}/config_info`,
    },

    PROJECT_GATEWAYS: {
        BASE: (projectName: IProject['project_name']) => `${API.BASE()}/project/${projectName}/gateways`,
        LIST: (projectName: IProject['project_name']) => `${API.PROJECT_GATEWAYS.BASE(projectName)}/list`,
        CREATE: (projectName: IProject['project_name']) => `${API.PROJECT_GATEWAYS.BASE(projectName)}/create`,
        DELETE: (projectName: IProject['project_name']) => `${API.PROJECT_GATEWAYS.BASE(projectName)}/delete`,
        DETAILS: (projectName: IProject['project_name']) => `${API.PROJECT_GATEWAYS.BASE(projectName)}/get`,
        SET_DEFAULT: (projectName: IProject['project_name']) => `${API.PROJECT_GATEWAYS.BASE(projectName)}/set_default`,
        SET_WILDCARD_DOMAIN: (projectName: IProject['project_name']) =>
            `${API.PROJECT_GATEWAYS.BASE(projectName)}/set_wildcard_domain`,

        // TEST_DOMAIN: (projectName: IProject['project_name'], instanceName: string) =>
        //     `${API.PROJECT_GATEWAYS.DETAILS(projectName, instanceName)}/test_domain`,
    },

    RUNS: {
        BASE: () => `${API.BASE()}/runs`,
        LIST: () => `${API.RUNS.BASE()}/list`,
    },
};
