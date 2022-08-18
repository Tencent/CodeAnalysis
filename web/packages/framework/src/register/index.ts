import { toPromise, info } from '@src/utils';

export interface LifeCycle<T> {
  bootstrap: (config: T) => Promise<any>;
  mount: (config: T) => Promise<any>;
  unmount: (config: T) => Promise<any>;
  update?: (config: T) => Promise<any>;
}

export interface RegistrableApp<T extends object> {
  name: string;
  lifeCycles: LifeCycle<T>;
}

/**
 *  微前端注册器
 */
export class MicroRegistration<T extends object> {
  private microApp: Map<string, RegistrableApp<T>> = new Map();

  // 注册微前端
  public register = (name: string, lifeCycles: LifeCycle<T>): void => {
    if (this.get(name)) {
      throw new Error(`存在重复微前端 ${name}，请检查该微前端名称`);
    }
    this.microApp.set(name, {
      name,
      lifeCycles: {
        bootstrap: toPromise(lifeCycles.bootstrap),
        mount: toPromise(lifeCycles.mount),
        unmount: toPromise(lifeCycles.unmount),
        update: toPromise(lifeCycles.update),
      },
    });
    info('注册微前端', name, '...');
  };

  public get = (name: string): RegistrableApp<T> | undefined => this.microApp.get(name);
}

export const registration = new MicroRegistration<any>();
