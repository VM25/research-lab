import { loadLabData } from "@/lib/data";
import Lab from "@/components/Lab";

export default async function Page() {
  const data = await loadLabData();
  return <Lab data={data} />;
}
