// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 无边框select-支持筛选、清除、label
 */

import React, { useState } from 'react';
// import cn from 'classnames';
import { isEmpty, find } from 'lodash';

import { Dropdown, Menu, Input } from 'coding-oa-uikit';
import CaretDown from 'coding-oa-uikit/lib/icon/CaretDown';
import RemoveSelected from 'coding-oa-uikit/lib/icon/RemoveSelected';

import style from './style.scss';

interface SelectProps {
  item: object;
  key: string;
  keyPath: Array<string>;
  domEvent: object;
}

interface DataProps {
  text: string;
  value: string;
}

interface IProps {
  selectedKeys: Array<string>;  // 指定当前选中的条目
  label?: string | boolean;  // label 展示，为 false 则表示无需展示 label
  allowClear?: boolean;  // 是否支持清除
  showSearch?: boolean; // 是否支持搜索
  placeholder?: string;  // 未选中条目时显示的内容
  searchPlaceholder?: string;  // 搜索框的 placeholder
  overlay?: React.ReactElement;  // 自定义菜单
  data?: Array<DataProps>; // 下拉菜单数据
  dropdownStyle?: object; // 下拉菜单样式
  selectedTextStyle?: object; // 被选中的文本的样式
  onSearch?: (searchValue: string) => void;  // 搜索框值变化时的回调
  onSelect: (e: SelectProps) => void;  // 被选中时调用
  onClear?: () => void;  // 清空已选项操作
}

const SelectDropdown = (props: IProps) => {
  const {
    selectedKeys,
    label,
    allowClear,
    showSearch,
    placeholder = '全部',
    searchPlaceholder,
    overlay,
    data,
    dropdownStyle,
    selectedTextStyle,
    onSearch,
    onSelect,
    onClear,
  } = props;

  const [visible, setVisible] = useState(false);
  const [searchValue, onChangeSearchValue] = useState('');

  const handleVisibleChange = (flag: boolean) => {
    setVisible(flag);
  };

  const handleMenuClick = (e: any) => {
    // 搜索时，下拉框不隐藏
    if (e.key !== 'search') {
      setVisible(false);
      onSelect(e);
    }

    // 清空已选项
    if (allowClear && onClear && e.key === 'clear') {
      onClear();
      return;
    }
  };

  const getTexts = () => {
    let text = '';
    selectedKeys.forEach((key: string) => {
      const item = find(data, { value: key });
      if (item) {
        text = text ? `${text},${item.text}` : item.text;
      }
    });

    return text;
  };

  return (
    <div className={style.dropdownContainer} style={{ ...dropdownStyle }}>
      <Dropdown
        visible={visible}
        onVisibleChange={handleVisibleChange}
        overlay={
          overlay || (
            <Menu
              onClick={handleMenuClick}
              selectedKeys={selectedKeys}
            >
              {
                showSearch && (
                  <Menu.Item key='search'>
                    <Input.Search
                      size='middle'
                      allowClear
                      placeholder={searchPlaceholder || '筛选'}
                      onChange={(e: any) => {
                        onChangeSearchValue(e.target.value);
                        onSearch?.(e);
                      }}
                    />
                  </Menu.Item>
                )
              }
              {
                allowClear && (
                  <Menu.Item key='clear'>
                    <span className={style.clear}>
                    <RemoveSelected className={style.clearIcon}/> 清除已选项
                    </span>
                  </Menu.Item>
                )
              }
              {
                data
                  ?.filter((item: DataProps) => item.text?.toLowerCase().includes(searchValue.toLowerCase()))
                  .map((item: any) => (
                    <Menu.Item key={item.value}>
                      {item.text}
                    </Menu.Item>
                  ))
              }
            </Menu>
          )
        }>
        <div className={style.content}>
          {
            label && (
              <span className={style.label}>{label}：</span>
            )
          }
          <div className={style.curText}>
            <span style={{ ...selectedTextStyle }}>
              {isEmpty(selectedKeys) && !getTexts() ? placeholder : getTexts()}
              </span>
            <CaretDown className={style.caretDownIcon} />
          </div>
        </div>
      </Dropdown>
    </div>
  );
};

export default SelectDropdown;
