
import React from 'react';
import { useHistory } from 'react-router-dom';
import { t } from '@src/utils/i18n';
import { Button } from 'coding-oa-uikit';
import { getMetaContent } from '@tencent/micro-frontend-shared/util';
import Bullhorn from 'coding-oa-uikit/lib/icon/Bullhorn';
import ArrowRight from 'coding-oa-uikit/lib/icon/CaretRight';
import ChevronUp from 'coding-oa-uikit/lib/icon/ArrowCircleUp';

// 项目内
import CodeBannerPng from '@src/images/code-banner.png';
import SystemModel from '@src/images/system-model.png';
import QrCode from '@src/images/wx-group.png';
import { isEnableManage } from '@plat/util';
import { getManageRouter } from '@src/utils/getRoutePath';
import routes from '@plat/routes';
import { SHOW_MANAGE_BTN, SHOW_GROUP_QR_CODE } from '@plat/modules/home';
import s from './style.scss';

// 开源地址
const GITHUB_URL = getMetaContent('GITHUB_URL');

// 客户端指引URL地址
const CLIENT_GUIDE_URL = getMetaContent('CLIENT_GUIDE_URL');

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
                type="link"
                onClick={() => {
                  history.push(router);
                }}
              >
                {t('立即体验')}
              </Button>
              {SHOW_MANAGE_BTN && isEnableManage() && (
                <Button
                  className={s.btn}
                  type="link"
                  onClick={() => {
                    history.push(getManageRouter());
                  }}
                >
                  {t('管理入口')}
                </Button>
              )}
              {GITHUB_URL && <Button
                className={s.secondBtn}
                type="link"
                href={GITHUB_URL}
                target="_blank"
              >
                {t('GitHub 开源')}
              </Button>}
            </div>
          </div>
          {SHOW_GROUP_QR_CODE && <div className={s.qrCodeArea}>
            <div className={s.qrCode}><img width={180} src={QrCode}/></div>
            <p className={s.invite}><ChevronUp /> 扫码加入开源交流群</p>
          </div>}
        </div>
      </div>
      {CLIENT_GUIDE_URL && <div className={s.infoSection}>
        <div className={s.sectionContainer}>
          <div className={s.info}>
            <div>
              <p className={s.attention}><Bullhorn /> 体验前必读</p>
              <h2 className={s.title}>客户端节点接入</h2>
              <p className={s.pContent}>
                团队专机资源一键接入，自主管控机器资源和编译环境。
                <br />
                分别提供客户端的二进制包和 Docker 镜像，可自由选择安装到专机中，
                <br />
                无需额外部署，方便专机快速接入。
              </p>
              <div className={s.btnArea}>
                <Button
                  className={s.btn}
                  type="link"
                  href={CLIENT_GUIDE_URL}
                  target="_blank"
                >
                  {t('节点接入指引')}<ArrowRight />
                </Button>
              </div>
            </div>
            <div><img src={SystemModel} style={{ width: 400 }} /></div>
          </div>
        </div>
      </div>}
    </>
  );
};

export default Banner;
