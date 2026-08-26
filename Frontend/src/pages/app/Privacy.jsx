import AppHeader from '../../components/app/AppHeader'

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
    <div className="min-h-svh bg-[radial-gradient(120%_60%_at_50%_0%,#131317_0%,#08080A_60%)] text-[#F5F5F7]">
      <AppHeader title="Privacy" backTo="/app/profile" />
      <div className="mx-auto max-w-[620px] px-6 pb-[60px] pt-5">
        <h1 className="mb-3.5 mt-2 text-[32px] font-bold leading-[1.08] tracking-[-0.024em]">
          What Glimpses does with faces.
        </h1>
        <div className="h-[22px]" />
        {PRIVACY_ITEMS.map((item) => (
          <div key={item.h} className="border-t border-white/[0.08] py-5">
            <div className="mb-2 text-[17px] font-semibold tracking-[-0.012em]">{item.h}</div>
            <div className="text-[15.5px] leading-[1.62] text-white/58 text-pretty">{item.b}</div>
          </div>
        ))}
        <div className="border-t border-white/[0.08]" />
      </div>
    </div>
  )
}

export default Privacy
