// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 无边框下拉框
 */

import React, { useState, useEffect, useRef } from 'react';
import cn from 'classnames';
import $ from 'jquery';
import { isArray, find, isEmpty } from 'lodash';
import { Select, Input } from 'coding-oa-uikit';
// import CaretDown from 'coding-oa-uikit/lib/icon/CaretDown';
import RemoveSelected from 'coding-oa-uikit/lib/icon/RemoveSelected';

import style from './style.scss';

const { Option } = Select;

interface SelectItem {
  value: any;
  text: string;
}
interface SelectBorderlessProps {
  className?: any;
  placeholder?: string;
  value?: any;
  data: SelectItem[];
  multiple?: boolean;
  showSearch?: boolean;
  allowClear?: boolean;
  onChange: (value: any) => void;
}

const SelectBorderless = (props: SelectBorderlessProps & any) => {
  const { data, value, placeholder = '', multiple, showSearch, allowClear, className, onChange, ...otherProps } = props;
  const ref = useRef(null);
  // eslint-disable-next-line
  const [_value, setValue] = useState<any>();
  const [dropdownVsb, setDropdownVsb] = useState(false);

  useEffect(() => {
    $(document).mouseup((e: any) => {
      if (ref?.current) {
        const $target = $(ref.current);
        if ( // 判断点击区域非目标元素 && 非目标元素子元素
          !$target.is(e.target)
          && $target.has(e.target).length === 0
        ) {
          setDropdownVsb(false);
        }
      }
    });

    return () => {
      $(document).off('mouseup');
    };
  }, []);


  const renderValue = (_value: any) => {
    if (isArray(_value)) {
      return _value
        .filter(key => find(data, { value: key }))
        .map(key => (find(data, { value: key }) ? find(data, { value: key }).text : key))
        .join(', ');
    }

    const item = find(data, { value: _value });
    return item ? item.text : _value;
  };

  const dropdownRender = (menu: React.ReactNode) => (
    <div>
      {
        showSearch && (
          <Input />
        )
      }
      {
        allowClear && (
          <div
            className={style.clearItem}
            onClick={() => {
              setValue(isArray(_value) ? [] : '');
              onChange?.(isArray(value) ? [] : '');
            }}
          >
            <RemoveSelected />
                            清除已选择项
          </div>
        )
      }
      {menu}
    </div>
  );

  const isNoValue = (value: any) => (isArray(value) ? isEmpty(value) : !value);

  return (
    <div
      className={cn(className, style.selectBorderless)}
      ref={ref}
      onClick={() => setDropdownVsb(!dropdownVsb)}
    >
      <span
        className={style.selection}
        title={renderValue(value || _value)}
      >
        {isNoValue(value) && isNoValue(_value) ? placeholder : renderValue(value || _value)}
      </span>
      <Select
        {...otherProps}
        showSearch={false}
        showArrow={true}
        bordered={false}
        dropdownMatchSelectWidth={false}
        // suffixIcon={<CaretDown />}
        mode={multiple ? 'multiple' : undefined}
        dropdownClassName={style.dropdown}
        getPopupContainer={() => ref?.current ?? document.body}
        open={dropdownVsb}
        value={value || _value}
        onChange={(value) => {
          setValue(value);
          onChange?.(value);
        }}
        dropdownRender={dropdownRender}
      >
        {data?.map((item: SelectItem) => (
          <Option value={item.value} key={item.value}>{item.text}</Option>
        ))}
      </Select>
    </div>
  );
};

export default SelectBorderless;
