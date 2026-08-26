import { useNavigate } from 'react-router-dom'
import ImageSlot from '../../components/common/ImageSlot'

const pipeline = [
  { n: 'STEP 01', t: 'Upload', b: 'Photos arrive from any attendee and land in event storage.' },
  { n: 'STEP 02', t: 'Index faces', b: 'Every face is indexed into a collection scoped to this event alone.' },
  { n: 'STEP 03', t: 'Search faces', b: "A joiner's selfie is searched against that event's index." },
  { n: 'STEP 04', t: 'Matched photos', b: 'Results appear in the gallery under Photos of me.' },
]

const properties = [
  { k: 'Serverless', v: 'No servers to run or scale. Capacity follows the upload burst and drops back to nothing.' },
  { k: 'Event-scoped', v: 'One face index per event. Nothing is compared, joined, or carried across events.' },
  { k: 'Async by design', v: 'Uploading, indexing, and searching are separate stages, so a slow photo never blocks the rest.' },
  { k: 'Removable', v: 'Deleting a selfie removes the face data behind it and future searches stop returning matches.' },
]

const stackGroups = [
  {
    label: 'Compute & Orchestration',
    items: [
      { name: 'AWS Lambda', slot: 'stack-aws-lambda' },
      { name: 'AWS Step Functions', slot: 'stack-aws-step-functions' },
    ],
  },
  { label: 'AI / ML', items: [{ name: 'Amazon Rekognition', slot: 'stack-amazon-rekognition' }] },
  {
    label: 'Storage & Data',
    items: [
      { name: 'Amazon S3', slot: 'stack-amazon-s3' },
      { name: 'Amazon DynamoDB', slot: 'stack-amazon-dynamodb' },
      { name: 'DynamoDB Streams', slot: 'stack-dynamodb-streams' },
    ],
  },
  {
    label: 'Networking & Delivery',
    items: [
      { name: 'Amazon API Gateway', slot: 'stack-amazon-api-gateway' },
      { name: 'Amazon CloudFront', slot: 'stack-amazon-cloudfront' },
      { name: 'AWS WAF', slot: 'stack-aws-waf' },
    ],
  },
  { label: 'Eventing', items: [{ name: 'Amazon EventBridge', slot: 'stack-amazon-eventbridge' }] },
  {
    label: 'Language & Tooling',
    items: [
      { name: 'Python', slot: 'stack-python' },
      { name: 'AWS Lambda Powertools', slot: 'stack-aws-lambda-powertools' },
      { name: 'Boto3', slot: 'stack-boto3' },
    ],
  },
  {
    label: 'Infrastructure & CI/CD',
    items: [
      { name: 'Terraform', slot: 'stack-terraform' },
      { name: 'Jenkins', slot: 'stack-jenkins' },
    ],
  },
]

function HowItWorks() {
  const navigate = useNavigate()

  return (
    <div className="mx-auto max-w-[1080px] px-5 py-14 sm:px-6 md:py-24">
      <div className="max-w-[700px]">
        <div className="mb-[22px] text-[12.5px] font-semibold uppercase tracking-[0.16em] text-[#FF9578]/90">
          How it works
        </div>
        <h1 className="text-[36px] font-bold leading-[1.04] tracking-[-0.034em] text-balance md:text-[56px]">
          From a thousand photos to yours.
        </h1>
      </div>
      <p className="mt-10 max-w-[720px] text-[19.5px] leading-[1.6] tracking-[-0.011em] text-white/66 text-pretty">
        Photos are scanned as soon as they are uploaded. Your selfie is matched against the faces found in that event, and only that event, so the photos you appear in are gathered for you without anyone tagging anything. Matching never reaches across events, and there is no list of you spanning the app.
      </p>

      <div className="mt-[72px] border-t border-white/[0.08] pt-[38px]">
        <div className="mb-[30px] text-xs font-bold uppercase tracking-[0.11em] text-white/40">The pipeline</div>
        <div className="flex flex-col md:flex-row md:items-stretch">
          {pipeline.map((p, i) => (
            <div key={p.n} className="flex flex-1 flex-col md:min-w-0 md:flex-row md:items-stretch">
              <div className="flex-1 rounded-2xl border border-[#FF7A59]/[0.22] bg-white/[0.04] p-[18px] pb-5">
                <div className="mb-3 flex items-center gap-2.5">
                  <div className="flex h-[22px] w-[22px] flex-none items-center justify-center rounded-[7px] border border-[#FF7A59]/40 bg-[#FF7A59]/[0.16] font-mono text-[11px] font-semibold text-[#FF9578]">
                    {i + 1}
                  </div>
                  <div className="flex-none whitespace-nowrap font-mono text-[11px] font-semibold uppercase tracking-[0.13em] text-[#FF9578]/85">
                    {p.n}
                  </div>
                </div>
                <div className="mb-[7px] text-[17px] font-semibold tracking-[-0.014em]">{p.t}</div>
                <div className="text-[13.5px] leading-[1.55] text-white/45 text-pretty">{p.b}</div>
              </div>
              {i < pipeline.length - 1 && (
                <div className="flex flex-none items-center justify-center py-2.5 text-[15px] text-[#FF7A59]/55 md:px-2 md:py-0">
                  <span className="md:hidden">↓</span>
                  <span className="hidden md:inline">→</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="mt-[74px] border-t border-white/[0.08] pt-[38px]">
        <div className="mb-[34px] text-xs font-bold uppercase tracking-[0.11em] text-white/40">Under the hood</div>
        <div className="grid grid-cols-1 items-start gap-14 md:grid-cols-[1.05fr_0.95fr]">
          <div className="flex flex-col gap-[22px]">
            <p className="text-[19px] leading-[1.62] tracking-[-0.008em] text-white/72 text-pretty">
              Glimpses is a fully serverless image retrieval system built on AWS. When photos are uploaded, each one is processed through Amazon Rekognition's{' '}
              <span className="font-mono text-[0.92em] font-semibold text-[#FF9578]">IndexFaces</span> API, which builds a searchable face index scoped to that single event; faces are never compared across different events.
            </p>
            <p className="text-[19px] leading-[1.62] tracking-[-0.008em] text-white/72 text-pretty">
              When someone joins with a selfie, Rekognition's{' '}
              <span className="font-mono text-[0.92em] font-semibold text-[#FF9578]">SearchFaces</span> API matches their face against that event's index to find every photo they appear in. The entire pipeline, from upload through indexing through matching, is orchestrated by AWS Step Functions.
            </p>
          </div>
          <div className="grid grid-cols-1 gap-px overflow-hidden rounded-2xl border border-white/[0.08] bg-white/[0.08]">
            {properties.map((pr) => (
              <div key={pr.k} className="flex flex-col gap-[7px] bg-[#0A0A0C] px-5 pb-5 pt-[18px]">
                <div className="font-mono text-[11px] font-semibold uppercase tracking-[0.12em] text-[#FF9578]/85">{pr.k}</div>
                <div className="text-[15px] leading-[1.55] text-white/60 text-pretty">{pr.v}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-[74px] border-t border-white/[0.08] pt-[38px]">
        <div className="mb-[34px] text-xs font-bold uppercase tracking-[0.11em] text-white/40">Tech stack</div>
        <div className="flex flex-col gap-[30px]">
          {stackGroups.map((g) => (
            <div key={g.label}>
              <div className="mb-3.5 text-[13.5px] font-semibold tracking-[0.01em] text-white/55">{g.label}</div>
              <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-3">
                {g.items.map((item) => (
                  <div
                    key={item.name}
                    className="flex min-h-[100px] items-center gap-3.5 rounded-2xl border border-white/[0.08] bg-white/[0.04] px-4 py-3.5"
                  >
                    <div className="h-[72px] w-[72px] flex-none overflow-hidden rounded-xl border border-white/[0.08] bg-white/[0.05]">
                      <ImageSlot src={`images/marketing/${item.slot}.png`} label="Logo" />
                    </div>
                    <div className="text-[15px] leading-[1.35] tracking-[-0.008em] text-white/90 text-pretty">{item.name}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-[78px] flex flex-wrap items-end justify-between gap-10 border-t border-white/[0.08] pt-11">
        <h2 className="text-[28px] font-bold leading-[1.08] tracking-[-0.028em] md:text-[38px]">
          See it on your own event.
        </h2>
        <button
          onClick={() => navigate('/signup')}
          className="flex-none whitespace-nowrap rounded-full bg-[#FF7A59] px-8 py-4 text-[16.5px] font-semibold text-[#200C05] transition-transform duration-100 ease-out active:scale-[0.97]"
        >
          Sign up
        </button>
      </div>
    </div>
  )
}

export default HowItWorks
