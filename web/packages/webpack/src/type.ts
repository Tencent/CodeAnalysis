export type Omit<T, K> = Pick<T, Exclude<keyof T, K>>;

export type StrBoolean = 'true'| 'false';
