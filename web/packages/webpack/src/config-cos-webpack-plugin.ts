/**
 * 腾讯云COS Webpack 插件，参考 webpack5-cos-plugin
 */
import chalk from 'chalk';
import zlib from 'zlib';
import { Buffer } from 'buffer';
import { Compiler, Compilation } from 'webpack';
import COS, { COSOptions, BucketParams, GetBucketParams, UploadBody, PutObjectParams, CosObject } from 'cos-nodejs-sdk-v5';
import { isTrue } from './util';
import { Omit, StrBoolean } from './type';

const { red, green } = chalk.bold;

/** 插件名称 */
const PLUGIN_NAME = 'CosWebpackPlugin';
/** 当前工作目录下当前package.json中的name */
const DEFAULT_PROJECT_NAME = process.env.npm_package_name;
/** 当前工作目录下当前package.json中的version */
const DEFAULT_PROJECT_VERSION = process.env.npm_package_version;
/** 默认排除资源正则 */
const DEFAULT_EXCLUDE = /^.*\.(html|txt|map)$/;
/** 默认根路径 */
const DEFAULT_BASE_DIR = 'webpack_auto_upload_tmp';
/** 默认重试次数 */
const DEFAULT_RETRY = 3;

/** 环境变量 */
const {
  WEBPACK_COS_SECRET_ID,
  WEBPACK_COS_SECRET_KEY,
  WEBPACK_COS_BUCKET,
  WEBPACK_COS_REGION,
  WEBPACK_COS_DOMAIN_TYPE,
  WEBPACK_COS_BASE_DIR,
  WEBPACK_COS_PROJECT_DIR,
  WEBPACK_COS_USE_VERSION,
  WEBPACK_COS_VERSION,
  WEBPACK_COS_IGNORE_ERROR,
  WEBPACK_COS_EXIST_CHECK,
  WEBPACK_COS_IGNORE_EXIST_CHECK_FILENAMES,
  WEBPACK_COS_REMOVE_MODE,
} = process.env;

interface AssetFile {
  /** 资源名称 */
  name: string;
  /** 资源内容 */
  content: string | Buffer;
}

interface CosWebpackPluginProps {
  /** cos初始化配置参数 */
  cos?: COSOptions & {
    DomainType: 'cos-internal' | 'cos'
  };
  /** bucket配置参数 */
  bucket?: BucketParams;
  /** 第一级目录，默认 webpack_auto_upload_tmp */
  baseDir?: string;
  /** 第二级目录，项目名称，默认 npm_package_name */
  project?: string;
  /** 第三级目录，版本，，仅在useVersion为true时生效，默认 npm_package_version*/
  version?: string;
  /** 是否将版本作为第三级目录，默认关闭 */
  useVersion?: StrBoolean;
  /** 文件存在校验，默认开启 */
  existCheck?: StrBoolean;
  /** 忽略文件存在校验文件名称列表，即强制上传 */
  ignoreExistCheckFileNames?: string[];
  /** 是否开启gzip压缩，默认开启 */
  gzip?: StrBoolean;
  /** 上传文件请求重试次数，默认3次 */
  retry?: number;
  /** 排除项，正则表达式，默认 /^.*\.html$/ */
  exclude?: RegExp;
  /** 是否开启 plugin 日志，默认关闭 */
  enableLog?: StrBoolean;
  /** 是否忽略插件错误，默认关闭 */
  ignoreError?: StrBoolean;
  /** 资源是否不输出到目录，默认打开 */
  removeMode?: StrBoolean;
  /** 是否上传 */
  uploadConfigJson?: StrBoolean;
  /** 上传资源文件时候的参数项 */
  options?: Omit<PutObjectParams, 'Bucket' | 'Region' | 'Key' | 'Body'>;
}

interface Config {
  /** cos初始化配置参数 */
  cos: COSOptions;
  /** bucket配置参数 */
  bucket: BucketParams;
  /** 第一级目录，默认 webpack_auto_upload_tmp */
  baseDir: string;
  /** 第二级目录，项目名称，默认 npm_package_name */
  project?: string;
  /** 第三级目录，版本，，仅在useVersion为true时生效，默认 npm_package_version*/
  version?: string;
  /** 是否将版本作为第三级目录，默认关闭 */
  useVersion: boolean;
  /** 文件存在校验，默认开启 */
  existCheck: boolean;
  /** 忽略文件存在校验文件名称列表，即强制上传 */
  ignoreExistCheckFileNames: string[];
  /** 是否开启gzip压缩，默认开启 */
  gzip: boolean;
  /** 上传文件请求重试次数，默认3次 */
  retry: number;
  /** 排除项，正则表达式，默认 /^.*\.html$/ */
  exclude: RegExp;
  /** 是否开启 plugin 日志，默认关闭 */
  enableLog: boolean;
  /** 是否忽略插件错误，默认关闭 */
  ignoreError: boolean;
  /** 资源是否不输出到目录，默认打开 */
  removeMode: boolean;
  /** 上传资源文件时候的参数项 */
  options?: Omit<PutObjectParams, 'Bucket' | 'Region' | 'Key' | 'Body'>;
}

/** cos webpack plugin */
class CosWebpackPlugin {
  /** 配置项 */
  config: Config;
  /** COS 客户端 */
  client: COS;
  /** 上传文件前缀 */
  uploadPrefix: string;

  constructor(options?: CosWebpackPluginProps) {
    const {
      cos, bucket, baseDir, project, version, useVersion, existCheck, ignoreExistCheckFileNames,
      gzip, retry, exclude, enableLog, ignoreError, removeMode, ...other
    }: CosWebpackPluginProps = options || {};
    // 获取 domain type
    const domainType = (cos?.DomainType || WEBPACK_COS_DOMAIN_TYPE) === 'cos-internal' ? WEBPACK_COS_DOMAIN_TYPE : 'cos';
    // 格式化配置文件，优先级 项目配置 > 环境变量配置
    this.config = {
      cos: {
        ...cos,
        SecretId: cos?.SecretId || WEBPACK_COS_SECRET_ID || '',
        SecretKey: cos?.SecretKey || WEBPACK_COS_SECRET_KEY || '',
        Domain: `{Bucket}.${domainType}.{Region}.tencentcos.cn`,
      },
      bucket: {
        ...bucket,
        Bucket: bucket?.Bucket || WEBPACK_COS_BUCKET || '',
        Region: bucket?.Region || WEBPACK_COS_REGION || '',
      },
      baseDir: baseDir || WEBPACK_COS_BASE_DIR || DEFAULT_BASE_DIR,
      project: project || WEBPACK_COS_PROJECT_DIR || DEFAULT_PROJECT_NAME,
      version: version || WEBPACK_COS_VERSION || DEFAULT_PROJECT_VERSION,
      useVersion: isTrue(useVersion || WEBPACK_COS_USE_VERSION || false),
      existCheck: isTrue(existCheck || WEBPACK_COS_EXIST_CHECK || true),
      ignoreExistCheckFileNames: ignoreExistCheckFileNames || WEBPACK_COS_IGNORE_EXIST_CHECK_FILENAMES?.split(',') || [],
      gzip: isTrue(gzip || true),
      retry: retry === undefined ? DEFAULT_RETRY : retry,
      exclude: exclude || DEFAULT_EXCLUDE,
      enableLog: isTrue(enableLog || false),
      ignoreError: isTrue(ignoreError || WEBPACK_COS_IGNORE_ERROR || false),
      removeMode: isTrue(removeMode || WEBPACK_COS_REMOVE_MODE || true),
      ...other,
    };

    this.uploadPrefix = calcUploadPrefix(this.config);

    this.debug('配置项:', this.config);
    this.debug('文件上传前缀:', this.uploadPrefix);

    // 插件必要参数校验
    if (!this.config.cos.SecretId) {
      throw new Error(`[${PLUGIN_NAME}]: 需要配置 COS SecretId`);
    }

    if (!this.config.cos.SecretKey) {
      throw new Error(`[${PLUGIN_NAME}]: 需要配置 COS SecretKey`);
    }

    if (!this.config.bucket.Bucket) {
      throw new Error(`[${PLUGIN_NAME}]: 需要配置 COS Bucket`);
    }

    if (!this.config.bucket.Region) {
      throw new Error(`[${PLUGIN_NAME}]: 需要配置 COS Region`);
    }

    /** 初始化腾讯云COS客户端 */
    this.client = new COS(this.config.cos);
  }

  apply(compiler: Compiler) {
    let assetFiles: AssetFile[] = [];

    // compiler.hooks.emit Compilation.assets will be frozen in future，因此改用 processAssets 时处理
    compiler.hooks.compilation.tap(PLUGIN_NAME, (compilation) => {
      compilation.hooks.processAssets.tap({
        name: PLUGIN_NAME,
        stage: Compilation.PROCESS_ASSETS_STAGE_REPORT,
      }, (assets) => {
        assetFiles = this.pickWaitUploadAssetFiles(assets);
      });
    });

    // 避免构建异常资源上传cos
    compiler.hooks.afterEmit.tapAsync(PLUGIN_NAME, (_, callback) => {
      if (assetFiles.length) {
        log(green(`COS 上传开始，资源总数${assetFiles.length}......`));
        this.uploadAssetFiles(assetFiles)
          .then(() => {
            log(green(`COS 上传完成，资源总数${assetFiles.length}\n`));
            callback();
          })
          .catch((err) => {
            const msg = red(`COS 上传出错... code: ${err.code} name: ${err.name} message: ${err.message}\n`);
            log(msg);
            if (!this.config.ignoreError) {
              throw new Error(msg);
            }
          });
      } else {
        callback();
      }
    });
  }

  /** 从资源中匹配待上传的资源文件 */
  private pickWaitUploadAssetFiles(assets: {
    [key: string]: {
      source(): string | Buffer;
    };
  }) {
    const assetFiles: AssetFile[] = [];
    Object.keys(assets).forEach((key) => {
      // 仅获取匹配到的资源
      if (!this.config.exclude.test(key)) {
        const assetSource = assets[key];
        assetFiles.push({
          name: key,
          content: assetSource.source(),
        });
        // 默认会移除资源避免生成到output目录
        this.config.removeMode && delete assets[key];
      }
    });
    return assetFiles;
  }

  /** 上传全部资源文件 */
  private uploadAssetFiles(files: AssetFile[]) {
    const fileCount = files.length;
    const promises: Promise<boolean>[] = [];
    files.forEach((file, idx) => {
      promises.push(this.uploadAssetFileByExistCheck(file, idx + 1, fileCount));
    });
    return Promise.all(promises);
  }

  /** 上传资源，需校验资源是否已存在 */
  private uploadAssetFileByExistCheck(file: AssetFile, idx: number, fileCount: number) {
    return new Promise<boolean>((resole, reject) => {
      const uploadName = this.getUploadName(file.name);
      if (!this.config.existCheck || this.config.ignoreExistCheckFileNames.includes(file.name)) {
        // 则直接上传文件
        this.uploadAssetFile(file, uploadName, idx, fileCount).then(resole)
          .catch(reject);
      } else {
        // 存在性校验
        this.getBucketByUploadName(uploadName).then((contents) => {
          if (contents?.length > 0) {
            const timeStr = getTimeStr(new Date(contents[0].LastModified));
            log(`${green('已存在, 免上传')} (上传于 ${timeStr}) ${idx}/${fileCount}: ${uploadName}`);
            resole(true);
          } else {
            throw new Error('没有找到文件，需要上传');
          }
        })
          .catch(() => {
            // 没有找到文件，则上传文件
            this.uploadAssetFile(file, uploadName, idx, fileCount).then(resole)
              .catch(reject);
          });
      }
    });
  }

  /** 上传资源 */
  private uploadAssetFile(file: AssetFile, uploadName: string, idx: number, fileCount: number) {
    let retryTime = 0;
    return new Promise<boolean>((resolve, reject) => {
      this.getFileContentBuffer(file.content).then((buffer) => {
        const uploadAction = () => {
          retryTime += 1;
          log(chalk.green(`开始上传 ${idx}/${fileCount}: ${retryTime > 1 ? `第${retryTime - 1}次重试` : ''}`), uploadName);
          this.uploadFileToBucket(uploadName, buffer)
            .then(() => {
              log(green(`上传成功 ${idx}/${fileCount}: ${uploadName}`));
              resolve(true);
            })
            .catch((err) => {
              if (retryTime < this.config.retry + 1) {
                // 每隔0.5s执行重试
                const timer = setTimeout(() => {
                  clearTimeout(timer);
                  uploadAction();
                }, 500);
              } else {
                reject(err);
              }
            });
        };
        uploadAction();
      })
        .catch(err => reject(err));
    });
  }

  /** 获取资源buffer */
  private getFileContentBuffer(content: string | Buffer) {
    if (this.config.gzip) {
      return new Promise<Buffer>((resolve, reject) => {
        zlib.gzip(Buffer.from(content), (err, result) => {
          if (err) {
            reject(err);
          } else {
            resolve(result);
          }
        });
      });
    }
    return Promise.resolve(Buffer.from(content));
  }

  /** 获取 Bucket 下的 Object 列表，用于获取待上传文件是否在bucket中 */
  private getBucketByUploadName(uploadName: string) {
    return this.getBucket({
      Prefix: uploadName,
      MaxKeys: 1,
      ...this.config.bucket,
    });
  }

  /** 获取 Bucket 下的 Object 列表 */
  private getBucket(params: GetBucketParams) {
    return new Promise<CosObject[]>((resolve, reject) => {
      this.client.getBucket(params, (err, data) => {
        if (err) {
          reject(err);
        } else {
          resolve(data.Contents);
        }
      });
    });
  }

  /** 获取上传Bucket Object所需参数  */
  private getPutObjectOptions = () => {
    if (this.config.gzip) {
      if (this.config.options) {
        this.config.options.ContentEncoding = 'gzip';
      } else {
        this.config.options = {
          ContentEncoding: 'gzip',
        };
      }
    }
    return this.config.options;
  };

  /** 上传文件到 Bucket */
  private uploadFileToBucket(uploadName: string, data: UploadBody) {
    const opt = this.getPutObjectOptions();
    return new Promise((resolve, reject) => {
      this.client.putObject({
        Key: uploadName,
        Body: data,
        ...this.config.bucket,
        ...opt,
      }, (err, data) => {
        if (err) {
          reject(err);
        } else {
          resolve(data);
        }
      });
    });
  }

  /** debug 日志 */
  private debug = (...rest: any[]) => {
    this.config.enableLog && log(...rest);
  };

  /** 根据file name 获取要上传的文件全称 */
  private getUploadName(name: string) {
    return `${this.uploadPrefix}/${name}`.replace('//', '/');
  }
}

export default CosWebpackPlugin;

/** 计算上传文件的前缀 */
const calcUploadPrefix = (config: Config) => {
  let prefix = config.baseDir;
  if (config.project) {
    prefix = `${prefix}/${config.project}`;
  }
  if (config.useVersion && config.version) {
    prefix = `${prefix}/${config.version}`;
  }
  return prefix;
};

/** 日志 */
const log = (...rest: any[]) => {
  console.log(chalk.bgMagenta(`[${PLUGIN_NAME}]:`), ...rest);
};

/** 当前时间 */
const getTimeStr = (d: Date) => `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()} ${d.getHours()}:${d.getMinutes()}`;

