import { info } from '@src/utils';
import './version-checking';

const GIT_REVISION = process.env.GIT_REVISION || '';

setTimeout(() => {
  info(`Framework 版本: ${GIT_REVISION || 'dirty'}`);
}, 0);
