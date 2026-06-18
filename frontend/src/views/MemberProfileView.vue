<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import MemberSelect from '../components/MemberSelect.vue'
import MetricCard from '../components/MetricCard.vue'
import StatusBanner from '../components/StatusBanner.vue'
import { useLoyaltyData } from '../stores/useLoyaltyData'

const { state, refreshAll, fetchMemberProfile } = useLoyaltyData()
const selectedMemberId = ref('')

const profile = computed(() => state.memberProfile)

const timelineEvents = computed(() => {
  if (!profile.value) return []
  const events = []

  for (const tx of profile.value.transactions) {
    events.push({
      id: `tx-${tx.id}`,
      type: 'transaction',
      txType: tx.type,
      time: tx.created_at,
      title: tx.type === 'earn' ? '消费积分' : tx.type === 'redeem' ? '礼品兑换' : '生日礼遇',
      description: tx.note,
      points: tx.points
    })
  }

  for (const th of profile.value.tier_history) {
    events.push({
      id: `tier-${th.id}`,
      type: 'tier',
      time: th.created_at,
      title: '等级变更',
      description: th.reason,
      fromTier: th.from_tier_name,
      toTier: th.to_tier_name
    })
  }

  events.sort((a, b) => new Date(b.time) - new Date(a.time))
  return events
})

onMounted(async () => {
  await refreshAll()
  if (state.members[0]) {
    selectedMemberId.value = state.members[0].id
  }
})

watch(selectedMemberId, async (newId) => {
  if (newId) {
    await fetchMemberProfile(Number(newId))
  }
})

function formatDateTime(timeStr) {
  const d = new Date(timeStr)
  const pad = (n) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function formatDate(timeStr) {
  const d = new Date(timeStr)
  const pad = (n) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function voucherStatusLabel(status) {
  const map = { unused: '未使用', used: '已使用', expired: '已过期' }
  return map[status] || status
}

function voucherStatusClass(status) {
  const map = { unused: 'success', used: 'neutral', expired: 'danger' }
  return map[status] || 'neutral'
}
</script>

<template>
  <section class="view-stack">
    <div class="section-header">
      <div>
        <p class="eyebrow">Member Profile</p>
        <h2>会员画像</h2>
      </div>
      <StatusBanner :error="state.error" :notice="state.notice" :loading="state.loading" />
    </div>

    <div class="toolbar-panel">
      <label style="gap: 0; font-weight: 400;">
        选择会员
        <MemberSelect v-model="selectedMemberId" :members="state.members" />
      </label>
      <div v-if="profile" class="member-brief">
        <span class="member-tier-badge">{{ profile.member.tier_name }}</span>
        <span class="member-phone">{{ profile.member.phone }}</span>
      </div>
      <div></div>
    </div>

    <template v-if="profile">
      <div class="metrics-grid">
        <MetricCard label="累计消费" :value="`¥${profile.stats.total_spent.toFixed(2)}`" hint="历史消费总金额" />
        <MetricCard label="当前积分" :value="profile.stats.total_points" hint="可用积分余额" />
        <MetricCard
          label="累计获得积分"
          :value="profile.stats.earn_points"
          :hint="`通过 ${profile.stats.earn_count} 次消费获得`"
        />
        <MetricCard
          label="已兑换积分"
          :value="profile.stats.redeem_points"
          :hint="`已兑换 ${profile.stats.redeem_count} 次礼品`"
        />
      </div>

      <div class="metrics-grid">
        <MetricCard
          label="礼券总数"
          :value="profile.stats.voucher_count"
          :hint="`未使用 ${profile.stats.unused_voucher_count} 张`"
        />
        <MetricCard
          label="会员等级"
          :value="profile.member.tier_name"
          :hint="`折扣 ${100 - profile.member.discount_percent > 100 ? '无' : (100 - profile.member.discount_percent) + '%'}`"
        />
        <MetricCard label="生日" :value="formatDate(profile.member.birthday)" hint="会员生日日期" />
        <MetricCard label="注册时间" :value="formatDate(profile.member.created_at)" hint="加入会员日期" />
      </div>

      <div class="two-column">
        <section class="panel">
          <h3>会员权益</h3>
          <div class="benefits-list">
            <span v-for="benefit in profile.member.benefits" :key="benefit" class="benefit-tag">
              {{ benefit }}
            </span>
          </div>

          <h3 style="margin-top: 24px;">礼券记录</h3>
          <div v-if="profile.vouchers.length === 0" class="empty-state">
            暂无礼券记录
          </div>
          <div v-else class="data-table">
            <div class="table-head voucher-cols">
              <span>名称</span>
              <span>内容</span>
              <span>发放时间</span>
              <span>过期时间</span>
              <span>状态</span>
            </div>
            <div v-for="v in profile.vouchers" :key="v.id" class="table-row voucher-cols">
              <span><strong>{{ v.title }}</strong></span>
              <span><small>{{ v.value }}</small></span>
              <span><small>{{ formatDate(v.issued_at) }}</small></span>
              <span><small>{{ formatDate(v.expires_at) }}</small></span>
              <span>
                <span class="status" :class="voucherStatusClass(v.status)">
                  {{ voucherStatusLabel(v.status) }}
                </span>
              </span>
            </div>
          </div>
        </section>

        <section class="panel">
          <h3>活动时间线</h3>
          <div v-if="timelineEvents.length === 0" class="empty-state">
            暂无活动记录
          </div>
          <div v-else class="timeline">
            <div v-for="event in timelineEvents" :key="event.id" class="timeline-item">
              <div class="timeline-dot" :class="event.type"></div>
              <div class="timeline-content">
                <div class="timeline-header">
                  <span class="timeline-title" :class="event.type">
                    {{ event.title }}
                  </span>
                  <span class="timeline-time">{{ formatDateTime(event.time) }}</span>
                </div>
                <p class="timeline-desc">{{ event.description }}</p>
                <div v-if="event.type === 'transaction'" class="timeline-points" :class="{ negative: event.points < 0 }">
                  {{ event.points > 0 ? '+' : '' }}{{ event.points }} 积分
                </div>
                <div v-if="event.type === 'tier'" class="timeline-tier">
                  <template v-if="event.fromTier">
                    <span class="tier-from">{{ event.fromTier }}</span>
                    <span class="tier-arrow">→</span>
                  </template>
                  <span class="tier-to">{{ event.toTier }}</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </template>

    <div v-else-if="state.members.length > 0 && !state.loading" class="panel">
      <p class="empty-state">请在上方选择会员查看画像</p>
    </div>
  </section>
</template>

<style scoped>
.member-brief {
  display: flex;
  gap: 12px;
  align-items: center;
}

.member-tier-badge {
  background: #c45f35;
  color: #fff;
  border-radius: 8px;
  padding: 6px 12px;
  font-weight: 800;
  font-size: 13px;
}

.member-phone {
  color: #6c6258;
  font-size: 14px;
}

.benefits-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.benefit-tag {
  background: #eef3e7;
  border-radius: 8px;
  color: #365a39;
  font-size: 13px;
  font-weight: 700;
  padding: 8px 12px;
}

.empty-state {
  color: #9a8f85;
  padding: 24px 0;
  text-align: center;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;
  padding-left: 8px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 11px;
  top: 8px;
  bottom: 8px;
  width: 2px;
  background: #e6dccd;
}

.timeline-item {
  display: grid;
  grid-template-columns: 24px 1fr;
  gap: 14px;
  padding: 12px 0;
  position: relative;
}

.timeline-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  margin-top: 4px;
  z-index: 1;
  border: 3px solid #fffdf8;
}

.timeline-dot.transaction {
  background: #2f7d50;
}

.timeline-dot.tier {
  background: #c45f35;
}

.timeline-content {
  display: grid;
  gap: 6px;
  padding-bottom: 4px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.timeline-title {
  font-weight: 800;
  font-size: 15px;
}

.timeline-title.transaction {
  color: #2f6f3f;
}

.timeline-title.tier {
  color: #a94f2c;
}

.timeline-time {
  color: #74695f;
  font-size: 12px;
  font-weight: 600;
}

.timeline-desc {
  margin: 0;
  color: #4d463f;
  font-size: 14px;
  line-height: 1.5;
}

.timeline-points {
  font-weight: 800;
  font-size: 14px;
  color: #2f7d50;
  justify-self: start;
}

.timeline-points.negative {
  color: #b74a32;
}

.timeline-tier {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 13px;
}

.tier-from {
  color: #74695f;
}

.tier-arrow {
  color: #9a8f85;
}

.tier-to {
  color: #c45f35;
  background: #fff1e8;
  padding: 4px 10px;
  border-radius: 6px;
}
</style>
