import React from 'react';
import { Tag, Tooltip } from 'coding-oa-uikit';
import { getMetaContent } from '@tencent/micro-frontend-shared/util';

// 模块内
import GitHubSvg from '@src/images/github.svg';
import LayoutHeader from '@src/component/layout-header';

// 通过meta版本名称来定义是否显示Tag
const VERSION_NAME = getMetaContent('VERSION_NAME');
// github url，用于标记是否显示开源地址
const GITHUB_URL = getMetaContent('GITHUB_URL');

const Header = () => <LayoutHeader
  leftContent={<>
    {VERSION_NAME && <Tag>{VERSION_NAME}</Tag>}
  </>}
  rightContent={<>
    {GITHUB_URL && <Tooltip placement='bottomLeft'
      title="我们开源啦(⁎⁍̴̛ᴗ⁍̴̛⁎)，点击访问开源地址" getPopupContainer={() => document.body}>
      <a style={{ marginRight: 20 }} href={GITHUB_URL} target='_blank' rel="noreferrer">
        <img width={25} src={GitHubSvg} />
      </a>
    </Tooltip>}
  </>} />;

export default Header;
