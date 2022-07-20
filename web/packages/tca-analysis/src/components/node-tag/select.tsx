import React from 'react';
import { isEmpty } from 'lodash';
import { Select, Tag } from 'coding-oa-uikit';
import { SelectProps, SelectValue } from 'coding-oa-uikit/lib/select';

import { TAG_TYPE_ENUM, TAG_TYPE_CHOICES } from './constants';

import style from './style.scss';

const { Option } = Select;

export interface TagSelectProps extends SelectProps<SelectValue> {
  orgSid: string;
  tags: any[];
}

/**
 * 运行环境选框
 */
const TagSelect = (props: TagSelectProps) => {
  const { orgSid, tags, ...other } = props;

  return (
  <Select
    getPopupContainer={() => document.body}
    optionFilterProp="label"
    showSearch
    {...other}
  >
    {tags.map(item => (
      (item.tag_type === TAG_TYPE_ENUM.PUBLIC)
      || (item.tag_type === null)
      || ((item.tag_type === TAG_TYPE_ENUM.PRIVATE) && (item.org_sid === orgSid))
    ) && (
      <Option key={item.name} value={item.name} label={isEmpty(item.display_name) ? item.name : item.display_name}>
        <div className={style.tagOption}>
          <span>{isEmpty(item.display_name) ? item.name : item.display_name}</span>
          {item.tag_type === TAG_TYPE_ENUM.PRIVATE
            ? <Tag className={style.privateTag}>{TAG_TYPE_CHOICES[TAG_TYPE_ENUM.PRIVATE]}</Tag>
            : <Tag className={style.publicTag}>{TAG_TYPE_CHOICES[TAG_TYPE_ENUM.PUBLIC]}</Tag>
          }
        </div>
      </Option>
    ))}
  </Select>
  );
};

export default TagSelect;
 