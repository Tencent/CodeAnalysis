# 【Go】单元测试有效性验证

## 背景

单元测试是用来对一个模块、一个函数或者一个类来进行正确性检验的测试工作。也是提升现网质量的最广泛最简单有效的方式。

但是在实际开发工作中，由于工作繁忙而遗漏或缺乏对单元测试的正确认识，有些开发盲目追求高覆盖率，没有对单元测试做断言，这样的单元测试用例属于无效用例。
为了检测此类无效用例，业务侧找来了代码分析介入，进行单元测试有效性验证。

## 需求

- 判断一个单元测试用例中是否存在断言。

### 示例


```go
// Bad case
func Test_Demo1(t *testing.T) {
}


// Good case
func Test_Demo2(t *testing.T) {
    assert.NoError(t, err)
}
```


## 快速体验

TCA 现已支持 Go 语言的单元测试有效行验证，可以在 TCA 分析方案中搜索勾选以下规则包，快速体验。

### 启用规则包
分析方案 -> 代码检查 -> 单元测试有效性验证 -> 启用/查看规则

### 支持框架


- Go语言官方单测框架testing
- [testify](https://github.com/stretchr/testify)
- [goconvey](https://github.com/smartystreets/goconvey)


### 扩展

更多语言更多单元测试框架支持，欢迎提 issue 进行咨询扩展。
