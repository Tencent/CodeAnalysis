import React, { ReactNode, useEffect, useMemo, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import classnames from 'classnames';
import { Layout, Menu, Button } from 'coding-oa-uikit';
import Aleft from 'coding-oa-uikit/lib/icon/Aleft';
import Aright from 'coding-oa-uikit/lib/icon/Aright';
// 项目内引用
import s from './style.scss';
import OpenLinkSvg from './open-link.svg';

const { Sider } = Layout;
const { SubMenu } = Menu;

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


const LayoutMenu = ({ menus, breakpoint, title, showTitleBottomBorder }: LayoutMenuProps) => {
  const [collapsed, setCollapsed] = useState(false);
  const [openKeys, setOpenKeys] = useState([]);
  const tmpCollapsed = useRef(false);

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

  // 当处理完 openKeys 后，再更新 collapse
  useEffect(() => {
    setCollapsed(tmpCollapsed.current);
  }, [openKeys]);

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
          return menu.regexMatch.test(window.location.pathname);
        }
        // 否则采用startsWith
        return window.location.pathname.startsWith(menu.link);
      }
      return false;
    });
    return menuFilters.length > 0 ? menuFilters[0].key : '';
  }, [aggMenuItems, window.location.pathname]);

  useEffect(() => {
    setOpenKeys(getMatchOpenKeys(menus, selectedKey, tmpCollapsed.current));
  }, [menus, selectedKey]);

  // SubMenu 菜单项展开控制
  const onOpenChange = (openKeys: string[]) => {
    setOpenKeys(openKeys);
  };

  // 触发响应式布局断点时的回调
  const onCollapse = (collapsed: any) => {
    tmpCollapsed.current = collapsed;
    // 待关闭扩展子项后再处理collapse
    if (collapsed) {
      setOpenKeys([]);
    } else {
      setOpenKeys(getMatchOpenKeys(menus, selectedKey, collapsed));
    }
  };

  // 渲染链接类型菜单项
  const renderLink = (menu: MenuItem, children: ReactNode) => {
    if (menu.link) {
      if (menu.open) {
        return (
          <a href={menu.link} target="_blank" rel="noreferrer">
            {children}
            {!collapsed && <img className={s.openLink} src={OpenLinkSvg} />}
          </a>
        );
      }
      return <Link to={menu.link}>{children}</Link>;
    }
    return <></>;
  };

  return <Layout className={classnames(s.menuLayout)}>
    <Sider
      className={s.menuLayoutAside}
      theme="light"
      width="220"
      breakpoint={breakpoint}
      onBreakpoint={onCollapse}
      collapsedWidth="56"
      collapsed={collapsed}
    >
      <div className={s.menuLayoutAsideBody}>
        {title && (
          <div
            className={classnames(
              s.asideTitle,
              showTitleBottomBorder ? s.asideTitleBottomBorder : '',
            )}
          >
            {title}
          </div>
        )}
        <Menu
          selectedKeys={[selectedKey]}
          openKeys={openKeys}
          onOpenChange={onOpenChange}
          className={s.menuLayoutItems}
          theme="light"
          mode="inline"
        >
          {menus.filter(menu => menu).map((menu) => {
            if (menu.divider) {
              return (
                <Menu.Divider
                  key={menu.key}
                  className={classnames(
                    s.menuDivider,
                    collapsed ? s.menuDividerCollapsed : '',
                  )}
                />
              );
            }
            if (menu.childrens) {
              return (
                <SubMenu
                  className={s.subMenu}
                  key={menu.key}
                  icon={menu.icon}
                  title={menu.title}
                >
                  {menu.childrens.filter(item => item).map(subMenu => subMenu.link && (
                    <Menu.Item
                      className={s.subItem}
                      key={subMenu.key}
                    >
                      {renderLink(subMenu, subMenu.title)}
                    </Menu.Item>
                  ))}
                </SubMenu>
              );
            }
            if (menu.link) {
              return (
                <Menu.Item
                  className={s.item}
                  key={menu.key}
                  title={menu.title}
                >
                  {renderLink(menu, <>{menu.icon}{!collapsed && menu.title}</>)}
                </Menu.Item>
              );
            }
            return <></>;
          })}
        </Menu>
      </div>
      {breakpoint && (
        <div className={s.menuLayoutCollapseCtrl}>
          <Button
            type="text"
            onClick={() => onCollapse(!collapsed)}
            icon={!collapsed ? <Aleft /> : <Aright />}
          />
        </div>
      )}
    </Sider>
  </Layout>;
};

export default LayoutMenu;
