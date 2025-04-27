import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { URLs } from '../const';

export const fetchUser = createAsyncThunk('user/fetchUser', async (_, thunkAPI) => {
    const response = await fetch(`${URLs.backendHost}/api/user/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
    });
    if (!response.ok) throw new Error('Failed to fetch user');
    return await response.json();
});

const initialState = {
    data: null,
    status: 'idle',
    error: null,
};

const userSlice = createSlice({
    name: 'user',
    initialState,
    reducers: {
        setUser(state, action) {
        state.data = action.payload;
        },
        clearUser(state) {
        state.data = null;
        },
    },
    extraReducers: (builder) => {
        builder
        .addCase(fetchUser.pending, (state) => {
            state.status = 'loading';
        })
        .addCase(fetchUser.fulfilled, (state, action) => {
            state.status = 'succeeded';
            state.data = action.payload;
        })
        .addCase(fetchUser.rejected, (state, action) => {
            state.status = 'failed';
            state.error = action.error.message;
        });
    },
});

export const { setUser, clearUser } = userSlice.actions;
export default userSlice.reducer;