/**
 * 首页
 * biz-start
 * 目前适用于全平台
 * biz-end
 */
import React from 'react';
import { Layout } from 'coding-oa-uikit';

// 项目内
import Container from '@src/component/container';
import Header from './header';
import Banner from './banner';
import Section from './section';
import Footer from './footer';
import s from './style.scss';

const Home = () => <Container>
  <div id="home" className={s.home}>
    <Header />
    <Layout.Content className={s.content}>
      <Banner />
      <Section />
    </Layout.Content>
    <Footer />
  </div>
</Container>;

export default Home;
