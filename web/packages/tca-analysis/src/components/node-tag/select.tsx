import React from 'react';
import { isEmpty } from 'lodash';
import { Select, Tag } from 'coding-oa-uikit';
import { SelectProps, SelectValue } from 'coding-oa-uikit/lib/select';

import { TAG_TYPE_ENUM, TAG_TYPE_CHOICES } from './constants';

import style from './style.scss';

const { Option } = Select;

export interface TagSelectProps extends SelectProps<SelectValue> {
  tags: any[];
}

const formatTypeTag = (tagType: number) => {
  switch (tagType) {
    case TAG_TYPE_ENUM.PUBLIC:
      return <Tag className={style.publicTag}>{TAG_TYPE_CHOICES[tagType]}</Tag>;
    case TAG_TYPE_ENUM.PRIVATE:
      return <Tag className={style.privateTag}>{TAG_TYPE_CHOICES[tagType]}</Tag>;
    case TAG_TYPE_ENUM.DISABLED:
      return <Tag color='error'>{TAG_TYPE_CHOICES[tagType]}</Tag>;
    default:
      return <Tag className={style.publicTag}>{TAG_TYPE_CHOICES[TAG_TYPE_ENUM.PUBLIC]}</Tag>;
  }
};

/**
 * 运行环境选框
 */
const TagSelect = (props: TagSelectProps) => {
  const { tags, ...other } = props;

  return (
  <Select
    getPopupContainer={() => document.body}
    optionFilterProp="label"
    showSearch
    {...other}
  >
    {tags.map(item => (
      <Option
        key={item.name}
        value={item.name}
        label={isEmpty(item.display_name) ? item.name : item.display_name}
        disabled={item.tag_type === TAG_TYPE_ENUM.DISABLED}
      >
        <div className={style.tagOption}>
          <span>{isEmpty(item.display_name) ? item.name : item.display_name}</span>
          {formatTypeTag(item.tag_type)}
        </div>
      </Option>
    ))}
  </Select>
  );
};

export default TagSelect;
