import React, { ReactNode, useEffect, useMemo, useState, useRef, useCallback } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import classnames from 'classnames';
import { useResponsive } from 'ahooks';
import { Layout, Menu, Button, Divider } from 'tdesign-react';
import { PageFirstIcon, PageLastIcon } from 'tdesign-icons-react';

import { openURL } from '@tencent/micro-frontend-shared/util';
// 项目内引用
import OpenLinkSvg from './open-link.svg';
import s from './style.scss';

const { MenuItem, SubMenu } = Menu;

const MenuLayoutExpanded = 'menu-layout-expanded';
const MiniMenuLayoutExpanded = 'mini-menu-layout-expanded';

export interface MenuItem {
  /** 菜单名称 */
  title: string;
  /** 菜单图标 */
  icon?: ReactNode;
  /** 菜单链接 */
  link?: string;
  /** 是否跳转打开链接 */
  open?: boolean;
  /** key */
  key: string;
  /** 子菜单 */
  childrens?: MenuItem[];
  /** 是否折叠，存在子菜单才生效，默认不折叠 */
  isFold?: boolean;
  /** 正则路由 */
  regexMatch?: RegExp;
  /** 是否存在分割线 */
  divider?: boolean;
}

interface LayoutMenuProps {
  /** 菜单项 */
  menus: MenuItem[],
  /** breakpoint */
  breakpoint?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl';
  /** 菜单标题 */
  title?: ReactNode;
  /** 是否菜单title下展示border */
  showTitleBottomBorder?: boolean;

}

/** 获取当前匹配的 openkeys */
const getMatchOpenKeys = (menus: MenuItem[], selectedKey: string, collapse: boolean) => {
  const menuFilters = menus.filter(menu => menu.childrens
    && ((!menu.isFold && !collapse) || menu.childrens.filter(({ key }) => key === selectedKey).length > 0));
  return menuFilters.map(menu => menu.key);
};

const LayoutMenu = ({ menus, breakpoint, title }: LayoutMenuProps) => {
  const [collapsed, setCollapsed] = useState(false);
  const [openKeys, setOpenKeys] = useState([]);
  const tmpCollapsed = useRef(false);
  const location = useLocation();
  const history = useHistory();
  const responsive = useResponsive();

  useEffect(() => {
    if (breakpoint) {
      setCollapsed(responsive[breakpoint] === false);
    }
  }, [responsive, breakpoint]);

  /** 跳转处理 */
  const navigateHandle = useCallback((menu: MenuItem) => {
    if (menu.link) {
      if (menu.open) {
        openURL(menu.link);
      } else {
        history.push(menu.link);
      }
    }
  }, [history]);

  // 控制菜单collapsed样式
  useEffect(() => {
    const node = document.getElementById('main-container');
    if (node) {
      if (collapsed) {
        node.classList.remove(MenuLayoutExpanded);
        if (!node.classList.contains(MiniMenuLayoutExpanded)) {
          node.classList.add(MiniMenuLayoutExpanded);
        }
      } else {
        node.classList.remove(MiniMenuLayoutExpanded);
        if (!node.classList.contains(MenuLayoutExpanded)) {
          node.classList.add(MenuLayoutExpanded);
        }
      }
    }
    return () => {
      if (node) {
        node.classList.remove(MenuLayoutExpanded);
        node.classList.remove(MiniMenuLayoutExpanded);
      }
    };
  }, [collapsed]);

  // 聚合菜单项
  const aggMenuItems = useMemo(() => {
    const items: Array<MenuItem> = [];
    menus.forEach((menus) => {
      if (menus.childrens) {
        items.push(...menus.childrens);
      } else {
        items.push(menus);
      }
    });
    return items.filter(item => item);
  }, [menus]);

  // 根据路由匹配选中项
  const selectedKey = useMemo(() => {
    const menuFilters = aggMenuItems.filter((menu) => {
      if (menu.link) {
        if (menu.regexMatch) {
          // 正则匹配
          return menu.regexMatch.test(location.pathname);
        }
        // 否则采用startsWith
        return location.pathname.startsWith(menu.link);
      }
      return false;
    });
    return menuFilters.length > 0 ? menuFilters[0].key : '';
  }, [aggMenuItems, location.pathname]);

  useEffect(() => {
    setOpenKeys(getMatchOpenKeys(menus, selectedKey, tmpCollapsed.current));
  }, [menus, selectedKey]);

  return <Layout className={classnames(s.asideLayout)}>
    <Menu
      style={{ flexShrink: 0, height: '100%' }}
      width="220px"
      theme="light"
      className={s.layoutMenu}
      collapsed={collapsed}
      value={selectedKey}
      expanded={openKeys}
      onExpand={values => setOpenKeys(values)}
      logo={title && <div className={s.layoutMenuTitle}>{title}</div>}
      operations={
        breakpoint && <div className='tca-text-right'>
          <Button variant="text" shape="square" icon={collapsed ? <PageLastIcon /> : <PageFirstIcon />} onClick={() => setCollapsed(!collapsed)} />
        </div>
      }
    >
      {menus.map((menu) => {
        // 中线
        if (menu.divider) {
          return <Divider className={s.layoutMenuDivider} key={menu.key}></Divider>;
        }

        // 子菜单
        if (menu.childrens?.length) {
          return <SubMenu
            className={s.layoutSubMenu}
            key={menu.key}
            value={menu.key}
            icon={menu.icon}
            title={menu.title}
          >
            {menu.childrens.map(subMenu => (<MenuItem
              className={s.layoutMenuItem}
              key={subMenu.key}
              value={subMenu.key}
              onClick={() => navigateHandle(subMenu)}
            >
              {subMenu.title} {menu.open && <img className={s.openLink} src={OpenLinkSvg} />}
            </MenuItem>))}
          </SubMenu>;
        }

        // 菜单项
        return <MenuItem
          className={s.layoutMenuItem}
          key={menu.key}
          value={menu.key}
          icon={menu.icon}
          onClick={() => navigateHandle(menu)}
        >
          {menu.title} {menu.open && <img className={s.layoutMenuItemOpenLink} src={OpenLinkSvg} />}
        </MenuItem>;
      })}
    </Menu>
  </Layout>;
};

export default LayoutMenu;
