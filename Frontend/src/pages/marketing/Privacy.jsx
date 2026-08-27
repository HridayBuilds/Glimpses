const PRIVACY_ITEMS = [
  {
    h: 'Every face in an event photo is analyzed',
    b: 'This includes people who never signed up for Glimpses. We turn each face into a code, not a name and not a copy of the photo, and use it only to sort photos within that one event.',
  },
  {
    h: 'A face record lives in exactly one event',
    b: "Nothing carries over between events. Being matched at one event doesn't tell Glimpses anything about another, and there's no master list of your face across the app.",
  },
  {
    h: 'Your profile selfie is yours to remove',
    b: 'Deleting your selfie stops all future matching right away. Photos you were already matched to stay where they are; nothing new gets added after that.',
  },
  {
    h: 'Your name and email stay on photos you uploaded',
    b: 'Even if you leave an event or are removed from it, your name and email stay attached to any photos you added, so others in the event can still see who they came from.',
  },
]

function Privacy() {
  return (
    <div className="mx-auto max-w-[1080px] px-5 py-14 sm:px-6 md:py-24">
      <div className="max-w-[660px]">
        <div className="mb-[22px] text-[12.5px] font-semibold uppercase tracking-[0.16em] text-[#FF9578]/90">
          Privacy
        </div>
        <h1 className="text-[36px] font-bold leading-[1.04] tracking-[-0.034em] text-balance md:text-[56px]">
          What Glimpses does with faces.
        </h1>
      </div>

      <div className="mt-14 max-w-[760px] border-t border-white/[0.08] pt-11">
        {PRIVACY_ITEMS.map((item) => (
          <div key={item.h} className="border-t border-white/[0.08] py-6 first:border-t-0 first:pt-0">
            <div className="mb-2 text-[19px] font-semibold tracking-[-0.014em]">{item.h}</div>
            <div className="text-[16px] leading-[1.62] text-white/58 text-pretty">{item.b}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Privacy
