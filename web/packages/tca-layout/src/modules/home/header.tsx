import React from 'react';
import { Tag, Tooltip, Button } from 'tdesign-react';
import { LogoGithubFilledIcon } from 'tdesign-icons-react';
import { getMetaContent } from '@tencent/micro-frontend-shared/util';
import LayoutHeader from '@tencent/micro-frontend-shared/tca/component/layout-header';

// 通过meta版本名称来定义是否显示Tag
const VERSION_NAME = getMetaContent('VERSION_NAME');
// github url，用于标记是否显示开源地址
const GITHUB_URL = getMetaContent('GITHUB_URL');

const Header = () => <LayoutHeader
  leftContent={<>
    {VERSION_NAME && <Tag>{VERSION_NAME}</Tag>}
  </>}
  rightContent={<>
    {GITHUB_URL && <Tooltip placement='bottom-left'
      content="我们开源啦(⁎⁍̴̛ᴗ⁍̴̛⁎)，点击访问开源地址">
      <Button className='tca-mr-lg'
        shape='square'
        size='large'
        variant='text'
        href={GITHUB_URL}
        target='_blank'
        icon={<LogoGithubFilledIcon />} />
    </Tooltip>}
  </>} />;

export default Header;
