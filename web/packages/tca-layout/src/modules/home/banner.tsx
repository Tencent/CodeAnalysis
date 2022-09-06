
import React from 'react';
import { useHistory } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button, Carousel } from 'coding-oa-uikit';
import { getMetaContent } from '@tencent/micro-frontend-shared/util';
import cn from 'classnames';

// 项目内
import CodeBannerPng from '@src/images/code-banner.png';
import { isEnableManage } from '@plat/util';
import { getManageRouter } from '@src/utils/getRoutePath';
import routes from '@plat/routes';
import { SHOW_MANAGE_BTN } from '@plat/modules/home';
import s from './style.scss';

// 开源地址
const GITHUB_URL = getMetaContent('GITHUB_URL');

// 获取当前第一个路由
const path = routes[0]?.path || '/';
const router = path instanceof Array ? path[0] : path;

const Banner = () => {
  const history = useHistory();
  const { t } = useTranslation();

  return (
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
        <Carousel autoplay>
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
                type="link"
                onClick={() => {
                  history.push(router);
                }}
              >
                {t('立即体验')}
              </Button>
              {SHOW_MANAGE_BTN && isEnableManage() && (
                <Button
                  className={cn(s.btn, 'ml-lg')}
                  type="link"
                  onClick={() => {
                    history.push(getManageRouter());
                  }}
                >
                  {t('管理入口')}
                </Button>
              )}
            </div>
          </div>
          {GITHUB_URL && <div className={s.info}>
            <h2 className={s.title}>我们开源啦</h2>
            <p className={s.pContent}>
              用心关注每行代码迭代、助力传承卓越代码文化！
              <br />
              精准跟踪管理代码分析发现的代码质量缺陷、代码规范、代码安全漏洞、无效代码，以及度量代码复杂度、重复代码、代码统计。
            </p>
            <div className={s.btnArea}>
              <Button
                className={s.btn}
                type="link"
                href={GITHUB_URL}
                target="_blank"
              >
                {t('开源地址')}
              </Button>
            </div>
          </div>}
        </Carousel>
      </div>
    </div>
  );
};

export default Banner;
