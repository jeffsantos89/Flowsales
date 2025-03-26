import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface SomeState {
    value: number;
}

const initialState: SomeState = {
    value: 0,
};

const someSlice = createSlice({
    name: 'some',
    initialState,
    reducers: {
        increment: (state) => {
            state.value += 1;
        },
        decrement: (state) => {
            state.value -= 1;
        },
        setValue: (state, action: PayloadAction<number>) => {
            state.value = action.payload;
        },
        reset: (state) => {
            state.value = initialState.value;
        },
    },
});

export const { increment, decrement, setValue, reset } = someSlice.actions;
export default someSlice.reducer;