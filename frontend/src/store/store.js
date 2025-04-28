import { configureStore } from '@reduxjs/toolkit';
import userReducer from './userSlice';
import { loadState, saveState } from './localStorage';

const preloadedState = loadState();

const store = configureStore({
  reducer: {
    user: userReducer,
  },
  preloadedState,
});

store.subscribe(() => {
  saveState({
    user: store.getState().user,
  });
});

export default store;