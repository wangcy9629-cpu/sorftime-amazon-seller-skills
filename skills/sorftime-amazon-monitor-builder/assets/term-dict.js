/* 词表字典（可按你的品类增删改）
   CN: 关键词英文 -> 工作台显示中文名
   NOISE: 反查噪音词（与品类无关的品牌词/拼写错误），命中即剔除 */
const CN = {
  'water bottle':'水瓶','64 oz water bottle':'64 盎司水瓶','64oz water bottle':'64oz 水瓶','64 oz insulated water bottle':'64 盎司保温水瓶',
  '64oz insulated water bottle':'64oz 保温水瓶','water bottle insulated':'保温水瓶','insulated water bottle':'保温水瓶','insulated water bottle with straw':'带吸管保温水瓶',
  'water bottles':'水瓶','waterbottle':'水瓶','water jug':'水壶','water jugs':'水壶','water jugs for sports':'运动水壶','sports water jug':'运动水壶',
  'gallon water bottle':'1 加仑水瓶','gallon water jug':'1 加仑水壶','gallon water':'1 加仑水壶','half gallon water bottle':'半加仑水瓶','half gallon water jug':'半加仑水壶',
  '1 gallon water bottle':'1 加仑水瓶','one gallon water bottle':'1 加仑水瓶','1gallon water bottle':'1加仑水瓶','1 gallon jug':'1 加仑壶',
  '1 gallon water jug':'1 加仑水壶','1 gallon water bottle insulated':'1 加仑保温水瓶','1 gallon insulated water jug':'1 加仑保温水壶',
  'gallon water bottle insulated':'1 加仑保温水瓶','insulated gallon water bottle':'1 加仑保温水瓶','gallon insulated water bottle':'1 加仑保温水瓶',
  'gallon jug water bottle':'1 加仑壶水瓶','gallon stainless steel water jug':'1 加仑不锈钢水壶','bottled water gallon':'1 加仑装瓶装水',
  'large water bottle':'大容量水瓶','big water bottle':'大号水瓶','large water jug':'大容量水壶','big water jug':'大号水壶','huge water bottle':'超大水瓶',
  'giant water bottle':'巨型水瓶','water bottle large':'大号水瓶','water bottle big':'大水瓶','water bottle 1 gallon':'1 加仑水瓶',
  'stainless steel water bottles':'不锈钢水瓶','metal water bottle':'金属水瓶','thermos':'保温瓶','thermos water bottle':'保温瓶水瓶',
  'insulated bottles':'保温瓶','insulated water jug':'保温水壶','collapsible water jug':'可折叠水壶','hydrojug':'HydroJug','hydro jug':'大水壶',
  'water cooler':'取水器','water cooler jug':'取水器水桶','beverage dispenser':'饮品取用器','drink dispenser':'饮品取用器','drink dispensers for parties':'派对饮品桶',
  'water dispenser':'取水器','water dispenser for 5 gallon bottle':'5 加仑桶取水器','5 gallon water dispenser':'5 加仑取水器','5 gallon water jug':'5 加仑水桶',
  '2 gallon water jug':'2 加仑水桶','camping water jug':'露营水壶','sports water bottle':'运动水瓶','football water bottle':'橄榄球水瓶','baseball water bottle':'棒球水瓶',
  'red water bottle':'红色水瓶','black water bottle':'黑色水瓶','purple water bottle':'紫色水瓶','water bottle purple':'紫色水瓶',
  'stanley':'STANLEY','stanley cup':'STANLEY 随行杯','stanley cups':'STANLEY 杯','stanley water bottle':'STANLEY 水瓶','stanley bottle':'STANLEY 水瓶',
  'stanley 64 oz':'STANLEY 64oz','64 oz stanley':'64oz STANLEY','stanley cooler':'STANLEY 冰桶','stanley thermos':'STANLEY 保温壶','stanley jug':'STANLEY 水壶',
  'stanley water jug':'STANLEY 水壶','stanley coffee mug':'STANLEY 咖啡杯','stanley coffee cup':'STANLEY 咖啡杯','stanley mug':'STANLEY 马克杯',
  'stanley accessories':'STANLEY 配件','stanley pink':'STANLEY 粉色','pink stanley':'粉色 STANLEY','stanley 40 oz':'STANLEY 40oz',
  'yeti':'YETI','yeti 64 oz water bottle':'YETI 64oz 水瓶','yeti 64 oz':'YETI 64oz','64 oz yeti':'64oz YETI','yeti 64':'YETI 64',
  'yeti with handle':'带把手 YETI','yeti cup with handle':'带把手 YETI 杯','yeti purple':'YETI 紫色','purple yeti':'紫色 YETI','yeti pace purple':'YETI Pace 紫',
  'yeti rambler straw':'YETI Rambler 吸管','yeti jug':'YETI 水壶','yeti gallon jug':'YETI 1加仑壶','yeti gallon':'YETI 1加仑','gallon yeti':'1加仑 YETI',
  'yeti ceramic':'YETI 陶瓷内胆','yeti ceramic lined':'YETI 陶瓷内胆壶','yeti water bottles':'YETI 水瓶','yeti 5l':'YETI 5L',
  'rtic jug':'RTIC 壶','rtic 1 gallon jug':'RTIC 1加仑壶','rtic gallon jug':'RTIC 1加仑壶','rtic half gallon jug':'RTIC 半加仑壶','rtic water bottle':'RTIC 水瓶',
  'rtic water bottle lid':'RTIC 水瓶盖','coldest water bottle':'Coldest 水瓶','coldest water bottle with handle':'带把手 Coldest 水瓶','ceramic water bottle':'陶瓷内胆水瓶',
  'double wall vacuum insulated bottles':'双层真空保温瓶','insulation vacuum':'真空保温','pitcher':'带盖供饮壶','pitchers':'带盖供饮壶(复)','pitcher with lid':'带盖供饮壶',
  'glass pitchers with handle and lid':'带把手玻璃供饮壶','igloo water jug':'Igloo 水壶','tumbler':'随行杯','purple insulated water bottle':'紫色保温水瓶',
  'water':'水瓶(泛)'
};

const NOISE = new Set([
  'sta','stanely','water h','waterh','ninja water','owala','owala freesip','owala 64 oz water bottle','owala 64 oz','64 oz owala','owala 64',
  'owala water bottle 40 oz','16 oz owala water bottle','gatorade jug','gatorade insulated water bottle','gatorade water bottle','gatorade water jug',
  'insulated gatorade bottles','gatorade water bottle stainless steel','large gatorade jug','the one ring','half and half','half & half',
  'purple tumbler','purple hydroflask','purple hydrojug','hydrojug purple','swell water bottle','zulu water bottles','dometic water jug',
  'hot water bottle','stanley quencher 30 oz tumbler','stanley iceflow flip straw','simple modern water bottle','copper water bottle','water bittle',
  'small yeti cup','cooler','coolers','can cooler','small cooler','igloo cooler','rtic coolers','rtic soft cooler','rtic road trip cooler','rtic lunch cooler',
  'water storage','water storage containers','dispensador de agua','termos para agua fria','water'
]);

module.exports={CN,NOISE};
