// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案 - 代码检查
 */
import React from 'react';

import { Row, Col } from 'tdesign-react';

import PackageCard from './pkg-card';

import style from './style.scss';

interface PackageListProps {
  readonly?: boolean;
  pkgs: any[];
  selectedPkgs: Array<number>;
  customPackage: any;
  updatePkg: (isAdd: boolean, id: number) => void;
  getDetailLink: (packageId: number) => string;
}

const pkgLayout = {
  xs: 6,
  sm: 6,
  md: 6,
  lg: 4,
  xl: 4,
  xxl: 3,
};

const PackageList = ({
  readonly = false,
  pkgs,
  selectedPkgs,
  customPackage,
  updatePkg,
  getDetailLink,
}: PackageListProps) => (
  <div className={style.pkgWrapper}>
    <Row gutter={[24, 24]}>
      <Col {...pkgLayout}>
        <PackageCard
          disabled={true}
          checked={true}
          item={customPackage}
          onChange={updatePkg}
          isCustomPkg={true}
          detailLink={getDetailLink(customPackage.id)}
        />
      </Col>
      {pkgs.map((item: any) => (
        <Col key={item.id} {...pkgLayout}>
          <PackageCard
            disabled={readonly}
            checked={selectedPkgs.includes(item.id)}
            item={item}
            onChange={updatePkg}
            detailLink={getDetailLink(item.id)}
          />
        </Col>
      ))}
    </Row>
  </div>
);

export default PackageList;
