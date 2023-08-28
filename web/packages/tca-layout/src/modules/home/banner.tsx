
import React from 'react';
import { useHistory } from 'react-router-dom';
import { t } from '@src/utils/i18n';
import { Button } from 'tdesign-react';
import ChevronUp from 'coding-oa-uikit/lib/icon/ArrowCircleUp';

// 项目内
import routes from '@plat/routes';
import { isEnableManage } from '@plat/util';
import { SHOW_MANAGE_BTN, SHOW_GROUP_QR_CODE } from '@plat/modules/home';

import CodeBannerPng from '@src/images/code-banner.png';
import QrCode from '@src/images/wx-group.png';
import { getManageRouter } from '@src/utils/getRoutePath';
import s from './style.scss';

// 获取当前第一个路由
const path = routes[0]?.path || '/';
const router = path instanceof Array ? path[0] : path;

const Banner = () => {
  const history = useHistory();

  return (
    <>
      <div className={s.bannerSection}>
        <div className={s.sectionBg}>
          <div className={s.bgBox}>
            <img
              className={s.pcImg}
              src={CodeBannerPng}
            />
          </div>
        </div>
        <div className={s.sectionContainer}>
          <div className={s.info}>
            <h2 className={s.title}>腾讯云代码分析</h2>
            <p className={s.pContent}>
              用心关注每行代码迭代、助力传承卓越代码文化！
              <br />
              精准跟踪管理代码分析发现的代码质量缺陷、代码规范、代码安全漏洞、无效代码，以及度量代码复杂度、重复代码、代码统计。
            </p>
            <div className={s.btnArea}>
              <Button
                className={s.btn}
                onClick={() => {
                  history.push(router);
                }}
              >
                {t('立即体验')}
              </Button>
              {SHOW_MANAGE_BTN && isEnableManage() && (
                <Button
                  className={s.btn}
                  variant='outline'
                  onClick={() => {
                    history.push(getManageRouter());
                  }}
                >
                  {t('管理入口')}
                </Button>
              )}
            </div>
          </div>
          {SHOW_GROUP_QR_CODE && <div className={s.qrCodeArea}>
            <div className={s.qrCode}><img width={180} src={QrCode} /></div>
            <p className={s.invite}><ChevronUp /> 扫码加入开源交流群</p>
          </div>}
        </div>
      </div>
    </>
  );
};

export default Banner;
