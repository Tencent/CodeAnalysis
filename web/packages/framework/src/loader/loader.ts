import MicroApplication from '@src/meta/application';

/**
 * 微前端数据加载器
 */
export interface MicroApplicationLoader {
  readonly enabled: () => Promise<boolean>;
  readonly loadMeta: (production?: MicroApplication[]) => Promise<MicroApplication[]>;
  readonly renderUI?: (production: MicroApplication[], development: MicroApplication[]) => void;
  readonly exit?: (reload: boolean) => void;
}
