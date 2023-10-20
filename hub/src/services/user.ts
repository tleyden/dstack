import { API } from 'api';
import { createApi } from '@reduxjs/toolkit/query/react';
import { fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import fetchBaseQueryHeaders from 'libs/fetchBaseQueryHeaders';

export const userApi = createApi({
    reducerPath: 'userApi',
    baseQuery: fetchBaseQuery({
        prepareHeaders: fetchBaseQueryHeaders,
    }),

    tagTypes: ['User'],

    endpoints: (builder) => ({
        getUserData: builder.query<IUser, Partial<IUserAuthData>>({
            query: () => {
                return {
                    url: API.USERS.CURRENT_USER(),
                    method: 'POST',
                };
            },
        }),

        getUserList: builder.query<IUser[], void>({
            query: () => {
                return {
                    url: API.USERS.LIST(),
                    method: 'POST',
                };
            },

            providesTags: (result) =>
                result ? [...result.map(({ username }) => ({ type: 'User' as const, id: username })), 'User'] : ['User'],
        }),

        getUser: builder.query<IUserWithCreds, { name: IUser['username'] }>({
            query: ({ name }) => {
                return {
                    url: API.USERS.DETAILS(),
                    method: 'POST',
                    body: {
                        username: name,
                    },
                };
            },

            providesTags: (result) => (result ? [{ type: 'User' as const, id: result.username }] : []),
        }),

        checkAuthToken: builder.mutation<IUser, { token: string }>({
            query: ({ token }) => ({
                url: API.USERS.CURRENT_USER(),
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            }),
        }),

        createUser: builder.mutation<IUser, Omit<IUser, 'id'>>({
            query: (user) => ({
                url: API.USERS.CREATE(),
                method: 'POST',
                body: user,
            }),

            invalidatesTags: (result) => [{ type: 'User' as const, id: result?.username }, 'User'],
        }),

        updateUser: builder.mutation<IUser, Partial<IUser> & Pick<IUser, 'username'>>({
            query: (user) => ({
                url: API.USERS.UPDATE(),
                method: 'POST',
                body: user,
            }),

            invalidatesTags: (result) => [{ type: 'User' as const, id: result?.username }],
        }),

        refreshToken: builder.mutation<IUserWithCreds, Pick<IUser, 'username'>>({
            query: ({ username }) => ({
                url: API.USERS.REFRESH_TOKEN(),
                method: 'POST',
                body: { username },
            }),

            invalidatesTags: (result, error, { username }) => [{ type: 'User' as const, id: username }],
        }),

        deleteUsers: builder.mutation<void, IUser['username'][]>({
            query: (userNames) => ({
                url: API.USERS.BASE(),
                method: 'DELETE',
                body: {
                    users: userNames,
                },
            }),

            invalidatesTags: ['User'],
        }),
    }),
});

export const {
    useGetUserDataQuery,
    useGetUserListQuery,
    useGetUserQuery,
    useCheckAuthTokenMutation,
    useCreateUserMutation,
    useDeleteUsersMutation,
    useUpdateUserMutation,
    useRefreshTokenMutation,
} = userApi;
