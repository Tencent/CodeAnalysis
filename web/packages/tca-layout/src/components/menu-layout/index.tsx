// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { ReactNode } from 'react';
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
  title: string;
  icon?: ReactNode;
  link?: string;
  open?: boolean; // 跳转
  key: string;
  childrens?: MenuItem[];
  regexMatch?: RegExp;
  divider?: boolean;
}

interface IProps {
  menus: MenuItem[];
  breakpoint?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl';
  title?: ReactNode;
  showTitleBottomBorder?: boolean;
}

interface IState {
  collapsed: boolean;
}

class MenuLayout extends React.Component<IProps, IState> {
  public state = {
    collapsed: false,
  };

  // eslint-disable-next-line @typescript-eslint/no-useless-constructor
  constructor(props: IProps) {
    super(props);
  }

  public componentDidMount() {
    this.onCollapse(this.state.collapsed);
  }

  /**
     * 菜单折叠时增加class用于控制container显示内容
     * @param collapsed 折叠
     */
  public onCollapse(collapsed: boolean) {
    this.setState(
      {
        collapsed,
      },
      () => {
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
      },
    );
  }

  /**
     * 聚合菜单项
     * @param menus 菜单项
     */
  public getMenuItems(menus: MenuItem[]) {
    const items: Array<MenuItem> = [];
    menus.forEach((menus) => {
      if (menus.childrens) {
        items.push(...menus.childrens);
      } else {
        items.push(menus);
      }
    });
    return items;
  }

  /**
     * 根据路由获取选中菜单
     * @param menus 菜单
     * @return key
     */
  public getSelectedKey(menus: MenuItem[]) {
    const newMenus = this.getMenuItems(menus);
    const menuFilters = newMenus.filter((menu) => {
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
  }

  /**
     * 默认获取所有sub菜单key
     * @param menus 菜单项
     */
  public getDefaultOpenKeys(menus: MenuItem[]) {
    const menuFilters = menus.filter(menu => menu.childrens);
    return menuFilters.map(menu => menu.key);
  }

  public renderLink(menu: MenuItem, children: ReactNode) {
    if (menu.link) {
      if (menu.open) {
        return (
          <a href={menu.link} target="_blank" rel="noreferrer">
            {children}
            {!this.state.collapsed && <img className={s.openLink} src={OpenLinkSvg} />}
          </a>
        );
      }
      return <Link to={menu.link}>{children}</Link>;
    }
    return <></>;
  }

  public render() {
    const { menus, breakpoint, title, showTitleBottomBorder } = this.props;
    const selectedKey = this.getSelectedKey(menus);
    return (
      <Layout className={classnames(s.menuLayout)}>
        <Sider
          className={s.menuLayoutAside}
          theme="light"
          width="220"
          breakpoint={breakpoint}
          collapsedWidth="56"
          collapsed={this.state.collapsed}
          onCollapse={(collapsed) => {
            this.onCollapse(collapsed);
          }}
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
              defaultOpenKeys={this.getDefaultOpenKeys(menus)}
              className={s.menuLayoutItems}
              theme="light"
              mode="inline"
            >
              {menus.map((menu) => {
                if (menu.divider) {
                  return (
                    <Menu.Divider
                      key={menu.key}
                      className={classnames(
                        s.menuDivider,
                        this.state.collapsed ? s.menuDividerCollapsed : '',
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
                      {menu.childrens.map(subMenu => subMenu.link && (
                        <Menu.Item
                          onClick={() => {
                            this.onCollapse(false);
                          }}
                          className={s.subItem}
                          key={subMenu.key}
                        >
                          {this.renderLink(
                            subMenu,
                            subMenu.title,
                          )}
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
                      {this.renderLink(
                        menu,
                        <>
                          {menu.icon}
                          {!this.state.collapsed && menu.title}
                        </>,
                      )}
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
                onClick={() => this.onCollapse(!this.state.collapsed)}
                icon={!this.state.collapsed ? <Aleft /> : <Aright />}
              />
            </div>
          )}
        </Sider>
      </Layout>
    );
  }

  public componentWillUnmount() {
    const node = document.getElementById('main-container');
    if (node) {
      node.classList.remove(MenuLayoutExpanded);
      node.classList.remove(MiniMenuLayoutExpanded);
    }
  }
}

export default MenuLayout;
