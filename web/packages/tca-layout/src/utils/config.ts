// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 用于codedog的一些基本配置
 */
import { t } from '@src/i18n/i18next';
import HomeSvg from '@src/images/home.svg';
import LogoIco from '@src/images/favicon.ico';

interface IEnterpriseInfo {
  name: string;
  link: string;
  main_link: string;
  logo: string;
  home_logo: string;
}

/**
 * 企业信息
 */
export const enterpriseInfo: IEnterpriseInfo = {
  name: `${t('腾讯云代码分析')}`,
  link: '/',
  main_link: '/repos',
  logo: LogoIco,
  home_logo: HomeSvg,
};
