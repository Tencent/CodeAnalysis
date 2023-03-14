/** antd form 表单代码库地址校验，避免注入 */
export const formScmURLSecValidate = () => ({
  validator(rule, value: string) {
    const reg = new RegExp(/[\\\n\s$&,;|<>`{(})'"]/);
    if (reg.test(value)) {
      return Promise.reject('代码库格式错误');
    }
    return Promise.resolve();
  },
});
