import React from 'react';
import cn from 'classnames';

import { Link } from 'react-router-dom';
import { Switch, Tooltip } from 'tdesign-react';
import { RootListIcon, Edit1Icon, InternetIcon, ChevronRightIcon } from 'tdesign-icons-react';

import style from './style.scss';

interface PackageCardProps {
  disabled: boolean;
  item: any;
  checked: boolean;
  onChange: (isAdd: boolean, id: number) => void;
  isCustomPkg?: boolean;
  detailLink: string;
}

const CUSTOM_PKG_INFO = {
  name: '自定义规则包',
  labels: ['自定义'],
  description: '自定义规则包中规则配置会默认覆盖其他官方包中相同规则的配置',
};

const PackageCard = (props: PackageCardProps) => {
  const { disabled, item, checked, onChange, isCustomPkg, detailLink } = props;

  const pkgInfo = isCustomPkg ? { ...item, ...CUSTOM_PKG_INFO } : item;

  return (
    <div className={cn(style.package, isCustomPkg && style.customPackage)}>
      <div className={style.header}>
        {pkgInfo.name.length > 18 ? (
          <Tooltip content={pkgInfo.name}>
            <span className={style.name}>{pkgInfo.name}</span>
          </Tooltip>
        ) : (
          <span className={style.name}>{pkgInfo.name}</span>
        )}

        <Switch
          disabled={disabled}
          value={checked}
          onChange={value => onChange(value, pkgInfo.id)}
        />
      </div>
      <div className={style.labelWrapper}>
        {
          pkgInfo.need_compile && (
            <span className={cn(style.label, style.build)}>
              需要编译
            </span>
          )
        }
        {pkgInfo.labels.map((label: any) => (
          <span key={label} className={style.label}>
            {label}
          </span>
        ))}
      </div>
      <div className={cn(style.description, style.common)}>
        <RootListIcon className={style.icon} />
        {pkgInfo.description && pkgInfo.description.length > 48 ? (
          <Tooltip content={pkgInfo.description}>
            <div className={style.paragraph}>
              {pkgInfo.description.substring(0, 48)}...
            </div>
          </Tooltip>
        ) : (
          <div className={style.paragraph}>
            {pkgInfo.description}
          </div>
        )}
      </div>
      {isCustomPkg ? <div className={cn(style.language, style.common)}>
          <Edit1Icon className={style.icon} />
          <p>自定义规则 {item.checkrule_count} 条</p>
        </div>
        : <div className={cn(style.language, style.common)}>
        <InternetIcon className={style.icon} />
        <div>
          适用于 {pkgInfo.languages.length} 种语言
          {pkgInfo.languages.join('、').length > 20 ? (
            <Tooltip content={pkgInfo.languages.join('、')}>
              <p className={style.languages}>{pkgInfo.languages.join('、')}</p>
            </Tooltip>
          ) : (
            <p className={style.languages}>{pkgInfo.languages.join('、')}</p>
          )}
        </div>
      </div>}
      <div className={style.footer}>
        <Link to={detailLink} >
          查看详细规则 <ChevronRightIcon />{' '}
        </Link>
      </div>
    </div>
  );
};

export default PackageCard;
