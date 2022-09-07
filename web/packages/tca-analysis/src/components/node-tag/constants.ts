export const TAG_TYPE_ENUM = {
  PUBLIC: 1,
  PRIVATE: 2,
  DISABLED: 99,
};

export const TAG_TYPE_CHOICES = {
  [TAG_TYPE_ENUM.PUBLIC]: '公共',
  [TAG_TYPE_ENUM.PRIVATE]: '团队',
  [TAG_TYPE_ENUM.DISABLED]: '停用',
};

export const TAG_TYPE_COLOR = {
  [TAG_TYPE_ENUM.PUBLIC]: '#2db7f5',
  [TAG_TYPE_ENUM.PRIVATE]: '#108ee9',
  [TAG_TYPE_ENUM.DISABLED]: 'default',
};
