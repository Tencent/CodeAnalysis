import React from 'react';
import { Breadcrumb } from 'coding-oa-uikit';
import { Link } from 'react-router-dom';
import AngleRight from 'coding-oa-uikit/lib/icon/AngleRight';
import s from './style.scss';
import { useSelector } from 'react-redux';
import { GbcState, BreadcrumbItem, ItemTypes } from './types';

const GlobalBreadcrumb = () => {
  const breadcrumbItems: BreadcrumbItem[] = useSelector<{
    GLOBAL_BREADCRUMB: GbcState;
  }, BreadcrumbItem[]>(state => state.GLOBAL_BREADCRUMB.data);
  if (Array.isArray(breadcrumbItems) && breadcrumbItems.length > 0) {
    return (
      <div className={s.breadcrumb}>
        <AngleRight className={s.arrow} />
        <Breadcrumb className=" inline-block">
          {breadcrumbItems.map((item) => {
            switch (item.type) {
              case ItemTypes.Link:
                return (
                  <Breadcrumb.Item key={item.key}>
                    <Link className={item.className} to={item.href}>
                      {item.text}
                    </Link>
                  </Breadcrumb.Item>
                );
              // case ItemTypes.Dropdown:
              //   <Breadcrumb.Item key={item.key}><a className={item.className}
              //  href={item.href}>{item.text}</a></Breadcrumb.Item>
              //   break;
              case ItemTypes.Custom:
                return (
                  <Breadcrumb.Item key={item.key}>
                    <span className={item.className}>{item.render()}</span>
                  </Breadcrumb.Item>
                );
              default:
                return (
                  <Breadcrumb.Item key={item.key}>
                    <span className={item.className}>{item.text}</span>
                  </Breadcrumb.Item>
                );
            }
          })}
        </Breadcrumb>
      </div>
    );
  }
  return <></>;
};

export default GlobalBreadcrumb;
