import wheat from "./crops/wheat.svg";
import chickpea from "./crops/chickpea.svg";
import mustard from "./crops/mustard.svg";
import potato from "./crops/potato.svg";
import watermelon from "./crops/watermelon.svg";
import cucumber from "./crops/cucumber.svg";
import muskmelon from "./crops/muskmelon.svg";
import moong from "./crops/moong.svg";

export const cropImages: Record<string, string> = {
  wheat,
  chickpea,
  mustard,
  potato,
  watermelon,
  cucumber,
  muskmelon,
  moong,
};

export function cropImage(cropId: string): string {
  return cropImages[cropId] ?? wheat;
}
