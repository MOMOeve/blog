/**
 * Mock API 占位层
 * -------------------------------------------------------
 * 所有「后续可接真服务」的接口在此统一声明形状。
 * 当前全部返回 Promise + 本地模拟数据，不发起真实网络请求。
 *
 * 约定：
 * - 成功：{ ok: true, data, meta? }
 * - 失败：{ ok: false, error: { code, message } }
 */

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function ok(data, meta) {
  return { ok: true, data, meta: meta || { mock: true, ts: Date.now() } }
}

function fail(code, message) {
  return { ok: false, error: { code, message } }
}

/**
 * POST /v1/location/resolve
 * 根据设备定位或手动选择解析种植区域
 *
 * Request:
 * {
 *   lat?: number,
 *   lng?: number,
 *   manual?: { province: string, city: string, district?: string }
 * }
 *
 * Response data:
 * {
 *   province: string,
 *   city: string,
 *   district: string,
 *   label: string,
 *   climateZone: string,
 *   suitableCrops: string[]
 * }
 */
async function resolveLocation(payload) {
  await delay(280)
  if (payload && payload.manual) {
    const m = payload.manual
    return ok({
      province: m.province,
      city: m.city,
      district: m.district || '',
      label: m.district ? `${m.city} · ${m.district}` : `${m.province} · ${m.city}`,
      climateZone: '亚热带湿润',
      suitableCrops: ['刺梨', '茶叶', '猕猴桃']
    })
  }
  return ok({
    province: '贵州',
    city: '六盘水',
    district: '',
    label: '贵州 · 六盘水',
    climateZone: '亚热带湿润',
    suitableCrops: ['刺梨', '茶叶']
  })
}

/**
 * POST /v1/ai/voice-qa
 * 语音问答（ASR + LLM）
 *
 * Request:
 * {
 *   audioTempPath?: string,  // wx.chooseMedia / RecorderManager 临时路径
 *   text?: string,           // 也可直接传文本
 *   location?: { province, city, district }
 * }
 *
 * Response data:
 * {
 *   transcript: string,
 *   answer: string,
 *   relatedTips: string[],
 *   confidence: number
 * }
 */
async function voiceQa(payload) {
  await delay(500)
  const q = (payload && (payload.text || payload.transcript)) || '刺梨现在怎么浇水？'
  return ok({
    transcript: q,
    answer:
      '花果期建议见干见湿：表土发白再浇，每次浇透但避免积水。遇连续阴雨注意清沟排水，减少根腐风险。',
    relatedTips: ['配合有机肥薄肥勤施', '巡查叶背蚜虫与白粉病', '高温时段避开正午喷药'],
    confidence: 0.86
  })
}

/**
 * POST /v1/ai/diagnose
 * 拍照诊病（图像识别 + 病虫害知识库）
 *
 * Request:
 * {
 *   imageTempPath: string,   // 相机/相册临时路径
 *   crop: 'cili',
 *   location?: { province, city, district }
 * }
 *
 * Response data:
 * {
 *   diseaseId: string,
 *   name: string,
 *   severity: 'low' | 'medium' | 'high',
 *   confidence: number,
 *   summary: string,
 *   symptoms: string[],
 *   treatments: { title: string, detail: string }[],
 *   productIds: string[]     // 可跳转商城商品
 * }
 */
async function diagnoseCrop(payload) {
  await delay(650)
  if (!payload || !payload.imageTempPath) {
    // 允许无图演示：返回默认病例
  }
  return ok({
    diseaseId: 'cili_powdery_mildew',
    name: '刺梨白粉病（疑似）',
    severity: 'medium',
    confidence: 0.78,
    summary: '叶片与嫩梢出现白色粉状物，湿度偏高时易扩散。建议及时清园并喷施对症药剂。',
    symptoms: ['叶面白色粉斑', '嫩梢皱缩', '严重时叶片早落'],
    treatments: [
      { title: '农业防治', detail: '清除病叶病梢，改善通风，降低园内湿度。' },
      { title: '化学防治', detail: '选用刺梨专用杀菌剂，按说明稀释喷雾，间隔 7–10 天。' }
    ],
    productIds: ['p3']
  })
}

/**
 * POST /v1/ai/grade
 * 刺梨视觉分级与建议卖价
 *
 * Request:
 * {
 *   imageTempPath: string,
 *   location?: { province, city, district },
 *   unit?: 'jin' | 'kg'
 * }
 *
 * Response data:
 * {
 *   grade: string,           // 如「一级」
 *   gradeCode: 'A' | 'B' | 'C',
 *   traits: string[],
 *   suggestPrice: number,
 *   unit: string,
 *   marketRef: { low: number, high: number },
 *   updatedAt: string
 * }
 */
async function gradeCili(payload) {
  await delay(700)
  return ok({
    grade: '一级',
    gradeCode: 'A',
    traits: ['新鲜度高', '果形均匀', '刺少饱满'],
    suggestPrice: 8.5,
    unit: '斤',
    marketRef: { low: 8.0, high: 9.0 },
    updatedAt: '09:30'
  })
}

/**
 * POST /v1/ai/verify
 * 对版验货（品种/外观一致性比对）
 *
 * Request:
 * {
 *   sampleImageTempPath: string,
 *   targetImageTempPath?: string,
 *   expectedVariety?: string
 * }
 *
 * Response data:
 * {
 *   matched: boolean,
 *   score: number,
 *   variety: string,
 *   notes: string[],
 *   riskFlags: string[]
 * }
 */
async function verifyVariety(payload) {
  await delay(600)
  return ok({
    matched: true,
    score: 0.91,
    variety: '贵农 5 号（对版）',
    notes: ['果刺密度接近样板', '果色黄绿过渡正常', '未见明显异品种混入'],
    riskFlags: []
  })
}

/**
 * GET /v1/market/quotes
 * 附近市场行情
 *
 * Query: { city?, district?, crop: 'cili' }
 *
 * Response data:
 * {
 *   updatedAt: string,
 *   items: { id, name, low, high, unit, change, trend }[]
 * }
 */
async function fetchMarketQuotes(query) {
  await delay(320)
  const { marketQuotes } = require('../data/mock')
  return ok({
    updatedAt: '09:30',
    items: marketQuotes
  })
}

/**
 * GET /v1/farming/today-advice
 * 今日农事建议
 *
 * Query: { location, crop: 'cili' }
 *
 * Response data:
 * {
 *   title: string,
 *   content: string,
 *   weather: string,
 *   timeHint: string,
 *   planId: string
 * }
 */
async function fetchTodayAdvice(query) {
  await delay(250)
  const loc = (query && query.location) || {}
  const place = loc.district || loc.city || '六盘水'
  return ok({
    title: '今日农事建议',
    content:
      '刺梨进入花果期，建议加强水分管理，保持土壤湿润，避免积水；及时巡查病虫害，早发现早防治。',
    weather: `${place}今日多云，18-26°C，适合农事操作。`,
    timeHint: '07:30',
    planId: 'plan-cili-flower'
  })
}

/**
 * GET /v1/farming/plan/:planId
 * 种植方案详情
 */
async function fetchPlantingPlan(planId) {
  await delay(300)
  return ok({
    id: planId || 'plan-cili-flower',
    title: '刺梨花果期管理方案',
    stages: [
      { name: '水分', detail: '见干见湿，雨后及时排水。' },
      { name: '施肥', detail: '薄肥勤施，增施钾肥促果。' },
      { name: '病虫', detail: '重点关注白粉病、蚜虫，早防早治。' },
      { name: '修剪', detail: '疏除过密枝，改善通风透光。' }
    ],
    calendar: ['周一：巡园', '周三：追肥', '周五：喷药（如需）']
  })
}

/**
 * POST /v1/listing/create
 * 去挂售
 *
 * Request:
 * {
 *   grade: string,
 *   price: number,
 *   unit: string,
 *   quantity: number,
 *   location: object,
 *   images?: string[]
 * }
 */
async function createListing(payload) {
  await delay(400)
  if (!payload || !payload.price) return fail('INVALID', '缺少挂售价格')
  return ok({
    listingId: 'list_' + Date.now(),
    status: 'published',
    ...payload
  })
}

/**
 * POST /v1/orders/create
 * 下单
 */
async function createOrder(payload) {
  await delay(350)
  return ok({
    orderId: 'o' + Date.now(),
    status: 'pending_pay',
    ...payload
  })
}

const mockApi = {
  resolveLocation,
  voiceQa,
  diagnoseCrop,
  gradeCili,
  verifyVariety,
  fetchMarketQuotes,
  fetchTodayAdvice,
  fetchPlantingPlan,
  createListing,
  createOrder
}

module.exports = { mockApi, ok, fail }
