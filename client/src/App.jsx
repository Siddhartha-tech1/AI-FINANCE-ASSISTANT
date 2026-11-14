import { useEffect, useState } from 'react'
import { api, clearToken, getToken, setToken } from './services/api.js'

const iconPaths = {
  overview: 'M4 13h6V4H4v9Zm0 7h6v-4H4v4Zm10 0h6v-9h-6v9Zm0-16v4h6V4h-6Z',
  transactions: 'M7 7h11m0 0-3-3m3 3-3 3M17 17H6m0 0 3 3m-3-3 3-3',
  budget: 'M4 6h16M7 3v6m10-6v6M5 10h14v10H5V10Zm3 3h3m2 0h3',
  analytics: 'M5 19V9m7 10V5m7 14v-7',
  insights: 'M9 18h6m-5 3h4m-7-6h10c-1.1-1.3-1.7-2.9-1.7-4.6 0-3-2.4-5.4-5.3-5.4s-5.3 2.4-5.3 5.4C5.7 12.1 6.3 13.7 7 15Z',
}

function Icon({ name, size = 20 }) {
  return <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d={iconPaths[name]} /></svg>
}

const sampleTransactions = [
  ['Fresh Basket', 'Groceries', 'Food', '-₹1,240', 'coral'],
  ['Acme Studio', 'Salary', 'Income', '+₹68,000', 'green'],
  ['Metro Rail', 'Commute', 'Transport', '-₹180', 'blue'],
]

export default function App() {
  const [active, setActive] = useState('Overview')
  const [menuOpen, setMenuOpen] = useState(false)
  const [authOpen, setAuthOpen] = useState(false)
  const [credentials, setCredentials] = useState({ name: '', email: '', password: '' })
  const [authMode, setAuthMode] = useState('login')
  const [user, setUser] = useState(null)
  const [recentTransactions, setRecentTransactions] = useState([])
  const [summary, setSummary] = useState(null)
  const [authError, setAuthError] = useState('')
  const [transactionOpen, setTransactionOpen] = useState(false)
  const [notice, setNotice] = useState('')
  const [transaction, setTransaction] = useState({ description: '', amount: '', date: new Date().toISOString().slice(0, 10), type: 'expense', category: 'Other' })
  const nav = [['Overview', 'overview'], ['Transactions', 'transactions'], ['Budgets', 'budget'], ['Analytics', 'analytics'], ['AI Insights', 'insights']]
  async function refreshDashboard() { const [nextSummary, transactionResult] = await Promise.all([api.summary(), api.transactions()]); setSummary(nextSummary); setRecentTransactions(transactionResult.transactions) }
  useEffect(() => { if (getToken()) api.me().then(result => { setUser(result.user); return refreshDashboard() }).catch(() => { clearToken(); setAuthOpen(true) }) }, [])
  async function signIn(event) { event.preventDefault(); setAuthError(''); try { const result = authMode === 'register' ? await api.register(credentials) : await api.login(credentials); setToken(result.access_token); setUser(result.user); setAuthOpen(false); setCredentials({ name: '', email: '', password: '' }); await refreshDashboard(); setNotice(authMode === 'register' ? 'Your account is ready.' : 'Welcome back.'); } catch (error) { setAuthError(error.message) } }
  async function signOut() { try { await api.logout() } catch (_) {} clearToken(); setUser(null); setSummary(null); setRecentTransactions([]); setAuthMode('login'); setAuthOpen(true) }
  function startTransaction() { if (!getToken()) { setNotice('Please sign in before adding a transaction.'); setAuthOpen(true); return } setTransactionOpen(true) }
  async function suggestCategory() { if (!transaction.description.trim()) { setNotice('Add a description before requesting a category suggestion.'); return } try { const prediction = await api.predictCategory(transaction.description); setTransaction({ ...transaction, category: prediction.predicted_category, predicted_category: prediction.predicted_category }); setNotice(`Suggested category: ${prediction.predicted_category}. You can still change it.`) } catch (error) { setNotice(error.message) } }
  async function addTransaction(event) { event.preventDefault(); try { await api.createTransaction({ ...transaction, amount: Number(transaction.amount) }); setTransactionOpen(false); await refreshDashboard(); setNotice('Transaction added.'); } catch (error) { setNotice(error.message) } }

  return <div className="min-h-screen bg-[#fff] text-[#1d1d1f]">
    <header className="sticky top-0 z-20 border-b border-black/[.08] bg-white/80 backdrop-blur-xl">
      <div className="mx-auto flex h-14 max-w-[1440px] items-center justify-between px-5 sm:px-8">
        <a className="flex items-center gap-2 font-semibold tracking-[-.04em]" href="#overview" aria-label="Clearway home">
          <span className="grid h-7 w-7 place-items-center rounded-full bg-[#1d1d1f] text-sm text-white">c</span>
          clearway
        </a>
        <nav className="hidden items-center gap-7 text-[12px] text-[#424245] md:flex" aria-label="Primary navigation">
          {nav.map(([label]) => <button className={active === label ? 'nav-active' : ''} onClick={() => setActive(label)} key={label}>{label}</button>)}
        </nav>
        <div className="flex items-center gap-2">
          <button className="icon-button hidden sm:grid" aria-label="Search"><span className="text-lg">⌕</span></button>
          {user ? <><button className="avatar" onClick={() => setAuthOpen(true)} aria-label="Account">{user.name.slice(0, 1).toUpperCase()}</button><button className="link-button" onClick={signOut}>Sign out</button></> : <button className="avatar" onClick={() => { setAuthMode('login'); setAuthOpen(true) }} aria-label="Sign in">Sign in</button>}
          <button className="icon-button grid md:hidden" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle navigation"><span className="text-lg">☰</span></button>
        </div>
      </div>
      {menuOpen && <nav className="border-t border-black/[.08] bg-white px-5 py-3 md:hidden" aria-label="Mobile navigation">
        {nav.map(([label]) => <button className="mobile-nav" onClick={() => { setActive(label); setMenuOpen(false) }} key={label}>{label}</button>)}
      </nav>}
    </header>

    <main className="mx-auto max-w-[1440px] px-5 pb-16 pt-10 sm:px-8 sm:pt-14">
      <section id="overview" className="mb-10 flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
        <div>
          <p className="eyebrow">YOUR FINANCES, SIMPLIFIED</p>
          <h1 className="mt-3 max-w-2xl text-[42px] font-semibold leading-[1.08] tracking-[-.055em] sm:text-[56px]">Everything in balance.</h1>
          <p className="mt-4 max-w-xl text-[17px] leading-7 text-[#6e6e73]">A clear view of your money, right when you need it.</p>
        </div>
        <button className="primary-button" onClick={startTransaction}><span className="text-xl leading-none">+</span> Add transaction</button>
      </section>

      <section className="hero-panel">
        <div className="hero-copy">
          <p className="eyebrow text-white/60">NOVEMBER 2026</p>
          <p className="mt-5 text-[17px] text-white/70">Available balance</p>
          <p className="mt-1 text-[47px] font-semibold leading-none tracking-[-.055em] sm:text-[64px]">₹{summary ? summary.balance.toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '42,860.00'}</p>
          <p className="mt-6 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-2 text-sm text-white"><span className="h-2 w-2 rounded-full bg-[#30d158]" />₹4,720 more than last month</p>
        </div>
        <div className="hero-orb" aria-hidden="true"><div /><div /><span>₹</span></div>
      </section>

      <section className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Metric label="Income" amount={summary ? `₹${summary.income.toLocaleString('en-IN')}` : '₹68,000'} detail="This month" tone="green" />
        <Metric label="Expenses" amount={summary ? `₹${summary.expenses.toLocaleString('en-IN')}` : '₹25,140'} detail="This month" tone="coral" />
        <Metric label="Budget remaining" amount={summary?.budget_remaining == null ? 'Set a budget' : `₹${summary.budget_remaining.toLocaleString('en-IN')}`} detail={summary?.budget_percentage_used == null ? 'No budget for this month' : `${summary.budget_percentage_used}% used`} tone="blue" />
        <Metric label="Daily average" amount="₹838" detail="Down 8% this week" tone="neutral" />
      </section>

      <section className="mt-12 grid gap-5 xl:grid-cols-[1.45fr_1fr]">
        <div className="card p-6 sm:p-7">
          <div className="flex items-start justify-between gap-4"><div><p className="card-kicker">SPENDING OVERVIEW</p><h2 className="mt-2 text-2xl font-semibold tracking-[-.035em]">Your monthly rhythm</h2></div><button className="secondary-button">View analytics</button></div>
          <div className="chart" aria-label="Monthly income and spending chart"><div className="chart-y"><span>₹70k</span><span>₹45k</span><span>₹20k</span><span>₹0</span></div><div className="chart-area"><div className="grid-line l1"/><div className="grid-line l2"/><div className="grid-line l3"/><svg viewBox="0 0 600 220" preserveAspectRatio="none" role="img"><path className="area" d="M0 150 C40 142,62 130,95 132 S150 82,190 100 S240 70,280 78 S330 44,370 64 S425 34,465 48 S520 8,600 28 L600 220 L0 220Z"/><path className="income-line" d="M0 150 C40 142,62 130,95 132 S150 82,190 100 S240 70,280 78 S330 44,370 64 S425 34,465 48 S520 8,600 28"/><path className="expense-line" d="M0 180 C40 171,70 177,105 158 S165 168,205 145 S270 153,310 130 S380 143,420 112 S500 119,600 86"/></svg><div className="chart-months"><span>Jun</span><span>Jul</span><span>Aug</span><span>Sep</span><span>Oct</span><span>Nov</span></div></div></div>
          <div className="mt-5 flex gap-5 text-sm text-[#6e6e73]"><span className="legend"><i className="bg-[#2997ff]" />Income</span><span className="legend"><i className="bg-[#ff6961]" />Expenses</span></div>
        </div>
        <div className="card p-6 sm:p-7"><p className="card-kicker">TOP CATEGORY</p><h2 className="mt-2 text-2xl font-semibold tracking-[-.035em]">Food & dining</h2><div className="donut-wrap"><div className="donut"><div><strong>₹8,460</strong><small>spent</small></div></div></div><div className="space-y-3"><Category label="Food" value="₹8,460" color="#ff6961" /><Category label="Transport" value="₹4,320" color="#0071e3" /><Category label="Shopping" value="₹3,740" color="#bf5af2" /></div></div>
      </section>

      <section className="mt-5 grid gap-5 xl:grid-cols-[1.45fr_1fr]">
        <div className="card overflow-hidden"><div className="flex items-center justify-between px-6 pb-2 pt-6 sm:px-7"><div><p className="card-kicker">RECENT ACTIVITY</p><h2 className="mt-2 text-2xl font-semibold tracking-[-.035em]">Latest transactions</h2></div><button className="link-button" onClick={() => setActive('Transactions')}>See all</button></div><div className="mt-4 overflow-x-auto"><table><thead><tr><th>Transaction</th><th>Category</th><th className="text-right">Amount</th></tr></thead><tbody>{(recentTransactions.length ? recentTransactions.slice(0, 3).map(item => [item.description, item.date, item.category, `${item.type === 'expense' ? '-' : '+'}₹${item.amount.toLocaleString('en-IN')}`, item.type === 'expense' ? 'coral' : 'green']) : sampleTransactions).map(([name, sub, category, amount, tone]) => <tr key={`${name}-${sub}`}><td><div className="transaction-name"><span className={`transaction-icon ${tone}`}>{name[0]}</span><span><strong>{name}</strong><small>{sub}</small></span></div></td><td><span className="chip">{category}</span></td><td className={`amount ${tone}`}>{amount}</td></tr>)}</tbody></table></div></div>
        <aside className="ai-panel"><span className="ai-symbol">✦</span><p className="eyebrow text-[#6e6e73]">CLEARWAY INTELLIGENCE</p><h2 className="mt-3 text-[28px] font-semibold leading-tight tracking-[-.04em]">A little insight goes a long way.</h2><p className="mt-3 text-[15px] leading-6 text-[#6e6e73]">Your Food spending is 12% lower than last month. You’re on track with your budget.</p><button className="secondary-button mt-6">Explore insights</button></aside>
      </section>
      <FeaturePage active={active} />
    </main>{notice && <div className="fixed bottom-5 right-5 z-40 rounded-xl bg-[#1d1d1f] px-4 py-3 text-sm text-white">{notice}<button className="ml-3" onClick={() => setNotice('')}>×</button></div>}{transactionOpen && <div className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-5"><form onSubmit={addTransaction} className="w-full max-w-sm rounded-2xl bg-white p-7"><h2 className="text-2xl font-semibold">Add transaction</h2><input className="mt-4 w-full rounded-lg border p-3" placeholder="Description" required value={transaction.description} onChange={e => setTransaction({...transaction, description:e.target.value})}/><button type="button" className="secondary-button mt-3" onClick={suggestCategory}>Suggest category</button><input className="mt-3 w-full rounded-lg border p-3" type="number" min="0.01" step="0.01" placeholder="Amount" required value={transaction.amount} onChange={e => setTransaction({...transaction, amount:e.target.value})}/><input className="mt-3 w-full rounded-lg border p-3" type="date" required value={transaction.date} onChange={e => setTransaction({...transaction, date:e.target.value})}/><select className="mt-3 w-full rounded-lg border p-3" value={transaction.type} onChange={e => setTransaction({...transaction, type:e.target.value})}><option value="expense">Expense</option><option value="income">Income</option></select><select className="mt-3 w-full rounded-lg border p-3" value={transaction.category} onChange={e => setTransaction({...transaction, category:e.target.value})}>{['Food','Transport','Shopping','Bills','Entertainment','Health','Education','Other'].map(x => <option key={x}>{x}</option>)}</select><div className="mt-5 flex justify-end gap-3"><button type="button" className="secondary-button" onClick={() => setTransactionOpen(false)}>Cancel</button><button className="primary-button">Save</button></div></form></div>}{authOpen && <div className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-5"><form onSubmit={signIn} className="w-full max-w-sm rounded-2xl bg-white p-7"><h2 className="text-2xl font-semibold">{authMode === 'register' ? 'Create your account.' : 'Welcome back.'}</h2><p className="mt-2 text-sm text-[#6e6e73]">{authMode === 'register' ? 'Start recording your finances in a private workspace.' : 'Sign in to view your real finances.'}</p>{authMode === 'register' && <input className="mt-6 w-full rounded-lg border p-3" placeholder="Your name" required value={credentials.name} onChange={e => setCredentials({ ...credentials, name: e.target.value })}/>}<input className={`${authMode === 'register' ? 'mt-3' : 'mt-6'} w-full rounded-lg border p-3`} type="email" placeholder="Email" required value={credentials.email} onChange={e => setCredentials({ ...credentials, email: e.target.value })}/><input className="mt-3 w-full rounded-lg border p-3" type="password" minLength="8" placeholder="Password (8 or more characters)" required value={credentials.password} onChange={e => setCredentials({ ...credentials, password: e.target.value })}/>{authError && <p className="mt-3 text-sm text-red-600">{authError}</p>}<div className="mt-5 flex justify-end gap-3"><button type="button" className="secondary-button" onClick={() => user ? setAuthOpen(false) : setAuthMode(authMode === 'register' ? 'login' : 'register')}>{user ? 'Cancel' : authMode === 'register' ? 'Sign in instead' : 'Create account'}</button><button className="primary-button">{authMode === 'register' ? 'Create account' : 'Sign in'}</button></div></form></div>}
  </div>
}

function Metric({ label, amount, detail, tone }) { return <article className="metric-card"><div className={`metric-mark ${tone}`} /><p>{label}</p><strong>{amount}</strong><small>{detail}</small></article> }
function Category({ label, value, color }) { return <div className="flex items-center justify-between text-sm"><span className="flex items-center gap-2.5"><i className="h-2.5 w-2.5 rounded-full" style={{backgroundColor: color}} />{label}</span><strong>{value}</strong></div> }

function FeaturePage({ active }) {
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [budget, setBudget] = useState({ month: new Date().toISOString().slice(0, 7), total_budget: '' })
  useEffect(() => {
    if (!getToken() || active === 'Overview') return
    const load = active === 'Transactions' ? api.transactions : active === 'Budgets' ? api.budgets : active === 'Analytics' ? api.categories : active === 'AI Insights' ? api.insights : null
    if (load) load().then(setResult).catch(error => setError(error.message))
  }, [active])
  if (active === 'Overview') return null
  if (active === 'Transactions') return <section className="mt-12 card overflow-hidden"><div className="px-6 pt-6 sm:px-7"><p className="card-kicker">TRANSACTIONS</p><h2 className="mt-2 text-2xl font-semibold tracking-[-.035em]">All recorded transactions</h2></div>{error ? <p className="p-6 text-red-600">{error}</p> : <div className="mt-4 overflow-x-auto"><table><thead><tr><th>Description</th><th>Date</th><th>Category</th><th className="text-right">Amount</th></tr></thead><tbody>{result?.transactions?.length ? result.transactions.map(item => <tr key={item.id}><td><strong>{item.description}</strong></td><td>{item.date}</td><td><span className="chip">{item.category}</span></td><td className={`text-right amount ${item.type === 'expense' ? 'coral' : 'green'}`}>{item.type === 'expense' ? '-' : '+'}₹{item.amount.toLocaleString('en-IN')}</td></tr>) : <tr><td colSpan="4" className="text-[#6e6e73]">No transactions have been recorded yet.</td></tr>}</tbody></table></div>}</section>
  if (active === 'AI Insights') return <section className="mt-12 card p-6 sm:p-7"><p className="card-kicker">AI INSIGHTS</p><h2 className="mt-2 text-2xl font-semibold tracking-[-.035em]">Your recorded-finance insights</h2>{error ? <p className="mt-4 text-red-600">{error}</p> : <div className="mt-4 space-y-3">{result?.insights?.length ? result.insights.map(item => <div key={item.title}><strong>{item.title}</strong><p className="text-[#6e6e73]">{item.message}</p></div>) : <p className="text-[#6e6e73]">No insights yet. Add transactions or a budget to see tailored observations.</p>}</div>}</section>
  if (active === 'Analytics') return <section className="mt-12 card p-6 sm:p-7"><p className="card-kicker">ANALYTICS</p><h2 className="mt-2 text-2xl font-semibold tracking-[-.035em]">Expense categories</h2>{error ? <p className="mt-4 text-red-600">{error}</p> : <div className="mt-5 space-y-3">{result?.categories?.length ? result.categories.map(item => <div className="flex justify-between" key={item.category}><span>{item.category}</span><strong>₹{item.amount.toLocaleString('en-IN')}</strong></div>) : <p className="text-[#6e6e73]">No expenses recorded for this month.</p>}</div>}</section>
  if (active === 'Budgets') return <section className="mt-12 card p-6 sm:p-7"><p className="card-kicker">BUDGETS</p><h2 className="mt-2 text-2xl font-semibold tracking-[-.035em]">Saved monthly budgets</h2><form className="mt-5 flex flex-wrap gap-3" onSubmit={async event => { event.preventDefault(); try { await api.createBudget({ ...budget, total_budget: Number(budget.total_budget), category_limits: {} }); setBudget({ ...budget, total_budget: '' }); setResult(await api.budgets()) } catch (error) { setError(error.message) } }}><input className="rounded-lg border p-3" type="month" value={budget.month} onChange={event => setBudget({ ...budget, month: event.target.value })} required /><input className="rounded-lg border p-3" type="number" min="0" step="0.01" value={budget.total_budget} onChange={event => setBudget({ ...budget, total_budget: event.target.value })} placeholder="Monthly amount" required /><button className="primary-button">Save budget</button></form>{error ? <p className="mt-4 text-red-600">{error}</p> : <div className="mt-5 space-y-3">{result?.budgets?.length ? result.budgets.map(item => <div className="flex justify-between" key={item.id}><span>{item.month}</span><strong>₹{item.total_budget.toLocaleString('en-IN')}</strong></div>) : <p className="text-[#6e6e73]">No budget has been created yet.</p>}</div>}</section>
  return <section className="mt-12 card p-6 sm:p-7"><p className="card-kicker">FINANCE CHAT</p><h2 className="mt-2 text-2xl font-semibold tracking-[-.035em]">Ask about your records</h2><form className="mt-5 flex gap-3" onSubmit={async event => { event.preventDefault(); try { const answer = await api.chat(message); setResult(answer) } catch (error) { setError(error.message) } }}><input className="min-w-0 flex-1 rounded-lg border p-3" value={message} onChange={event => setMessage(event.target.value)} placeholder="How much did I spend?" required /><button className="primary-button">Ask</button></form>{error && <p className="mt-4 text-red-600">{error}</p>}{result?.answer && <p className="mt-4 text-[#424245]">{result.answer}</p>}</section>
}
