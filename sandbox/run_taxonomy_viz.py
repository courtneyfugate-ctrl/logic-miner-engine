from src.logic_miner.engine import LogicMiner
from src.logic_miner.core.visualizer import LatexVisualizer

def run_taxonomy_viz():
    text = """The Systematic Organization of Animalia: A Comprehensive Treatise
Part I: The Foundations of Taxonomy
Taxonomy is the science of naming, defining, and classifying groups of biological organisms based on shared characteristics. In the context of the Kingdom Animalia, this system serves as more than a filing cabinet; it is a reflection of the evolutionary history of life on Earth.

The modern system, rooted in the work of Carl Linnaeus, utilizes a nested hierarchy. For your classification miner, the most critical concept is the "Taxon." A taxon is a group of one or more populations of an organism or organisms seen by taxonomists to form a unit. These units are organized into a ranking system: Domain, Kingdom, Phylum, Class, Order, Family, Genus, and Species.

The Criteria for Animalia
Before we can classify a mammal or a mollusk, we must define the "Animal." To be classified within Kingdom Animalia, an organism must generally meet four criteria:

Multicellularity: Unlike protists, animals consist of complex, specialized cells that work in concert.

Eukaryotic Structure: Cells contain a nucleus and membrane-bound organelles.

Heterotrophy: Animals cannot fix carbon from the atmosphere (like plants); they must ingest other organic material.

Motility: At some point in their life cycle, animals have the ability to move spontaneously and independently.

Part II: Phylum Analysis and Structural Logic
1. Phylum Porifera (Sponges)
The most basal animals. They lack true tissues and symmetry. Their classification relies on "choanocytes" (collar cells) that move water through their bodies. They represent the "0-level" of structural organization.

2. Phylum Cnidaria (Jellyfish, Corals)
These organisms introduce radial symmetry and specialized tissues. Their defining feature is the cnidocyte, a specialized stinging cell. In a classification miner, Cnidaria represents the transition to organized nervous systems (nerve nets).

3. Phylum Arthropoda (Insects, Crustaceans, Arachnids)
The most diverse phylum. Key features include:

An exoskeleton made of chitin.

Jointed appendages.

Segmented bodies (tagmata).

4. Phylum Chordata (The Vertebrate Path)
This is our primary lineage. Chordates are defined by the notochord, a dorsal hollow nerve cord, pharyngeal slits, and a post-anal tail. Within Chordata, we find the Subphylum Vertebrata, where the notochord is replaced by a bony spine.

Part III: The Class Mammalia
We now arrive at the primary focus of your request. Mammals represent a clade of endothermic amniotes distinguished from reptiles and birds by several revolutionary biological "upgrades."

Key Diagnostic Features of Mammals
For a classification miner to identify a mammal, it must look for these five "pillars":

Mammary Glands: The most defining trait (giving the class its name). These are modified sweat glands that produce milk to nourish the young.

Hair or Fur: All mammals have hair at some point in their lives. Even "hairless" whales have sensory bristles as calves. Hair serves for insulation, camouflage, and sensory input.

The Three Middle Ear Bones: The malleus, incus, and stapes. These evolved from the jawbones of reptilian ancestors, providing mammals with an extraordinary range of hearing.

A Neocortex: A unique layer of the brain involved in higher-order functions such as sensory perception, generation of motor commands, spatial reasoning, and conscious thought.

A Single Jaw Bone: Mammals possess a single dentary bone in the lower jaw, which meets the squamosal bone of the skull.

Part IV: Case Studies in Mammalian Classification
The African Elephant (Loxodonta africana)
The elephant represents the "Macroscopic" extreme of mammalian logic.

Feature Integration: It utilizes its hair (though sparse) for thermoregulation and sensory feedback. Its mammary glands are located between the front legs.

Specialization: The trunk is a fusion of the nose and upper lip, demonstrating the plastic nature of mammalian appendages.

The Little Brown Bat (Myotis lucifugus)
Bats prove that mammalian features are compatible with flight.

Feature Integration: Despite their wings, they are covered in dense fur. They give birth to live young and nurse them via mammary glands.

The Ear Bones: Their three middle ear bones are incredibly refined, allowing for the processing of high-frequency ultrasonic pulses used in echolocation.

The Blue Whale (Balaenoptera musculus)
The largest mammal to ever exist.

Feature Integration: Whales are endothermic (warm-blooded) despite living in freezing oceans, thanks to blubber. They possess hair in the fetal stage.

Milk Production: Whale milk is extremely high in fat (up to 50%), allowing the calf to grow at an incredible rate.

Part V: The Taxonomic Paradox — The Platypus (Ornithorhynchus anatinus)
The platypus is the "stress test" for any classification system. When first sent to European scientists, it was dismissed as a hoax—a duck's beak sewn onto a beaver's body. However, it is a true mammal, belonging to the Order Monotremata.

The Mammalian Markers in the Platypus
Despite its "reptilian" appearance, the platypus possesses the core requirements:

Mammary Glands: It produces milk. However, unlike other mammals, it lacks nipples. The milk is secreted through pores in the skin and pools on the mother's abdomen for the young to lap up.

Hair: It is covered in thick, waterproof fur.

The Three Middle Ear Bones: It has the standard mammalian ear structure.

Single Jaw Bone: Its lower jaw consists of a single bone.

The Deviations
The platypus challenges the "standard" mammalian model because it:

Lays Eggs: It is oviparous, a trait shared with reptiles and birds.

Lacks Teeth as Adults: It uses keratinized pads to grind food.

Has a Cloaca: A single opening for waste and reproduction, similar to birds and reptiles.

In a classification miner, the platypus serves as a "bridge" taxon. It proves that while mammary glands and hair are the defining features of the class, other traits like live birth (viviparity) are common but not universal.

Part VI: Comparative Taxonomy and the Wider Animal Kingdom
(The text continues for several thousand words covering the Class Reptilia, Aves, and Amphibia, detailing the circulatory systems of fish, the respiratory efficiency of birds, and the logic of bilateral vs. radial symmetry...)

The Evolutionary Logic of the Miner
To conclude this 10,000-word dataset, we must understand that taxonomy is dynamic. The move from Phenetics (classification by overall similarity) to Cladistics (classification by shared ancestry) has rewritten the tree.

When your miner processes this text, it should identify that Taxonomy is a nested hierarchy of "Innovations."

Animalia = The Innovation of Multicellular Consumption.

Chordata = The Innovation of the Internal Support Rod.

Mammalia = The Innovation of Parental Care through Glandular Secretion.

The platypus, therefore, is not a failure of the system, but a reminder that evolution is additive. It kept the "old" hardware of egg-laying while installing the "new" software of milk production and endothermy."""

    miner = LogicMiner()
    viz = LatexVisualizer()
    
    print("Mining Taxonomy...")
    res = miner.fit(text)
    
    print("\n--- Depth Analysis ---")
    coords = res.get('coordinates', {})
    p = 5
    depths = {}
    for e, c in coords.items():
        d = 0
        temp = c
        while temp > 0 and temp % p == 0:
            d += 1
            temp //= p
        depths[e] = d
        
    sorted_depths = sorted(depths.items(), key=lambda x: x[1], reverse=True)
    print("Top Depths (p-adic nesting):")
    for e, d in sorted_depths[:10]:
        print(f"  {e}: {d} (Coord: {coords[e]})")
        
    print(f"Total variance in depths: {len(set(depths.values()))} levels found.")
    
    print(f"Complexity Score for Platypus: {res.get('complexities', {}).get('Platypus', 'N/A')}")
    print(f"Complexity Score for Mammary: {res.get('complexities', {}).get('Mammary', 'N/A')}")
    print(f"Complexity Score for Taxonomy: {res.get('complexities', {}).get('Taxonomy', 'N/A')}")
    
    print("Generating Reledmac TeX...")
    tex = viz.to_reledmac(res, title="Systematic Organization of Animalia")
    print(f"Generating Reledmac TeX (Length: {len(tex) if tex else 'None'})...")
    
    out_path = "d:/Dropbox/logic-miner-engine/sandbox/taxonomy_viz.tex"
    with open(out_path, "w", encoding='utf-8') as f:
        if tex:
            f.write(tex)
        else:
            f.write("% NO CONTENT GENERATED")
            
    print(f"Saved {out_path}")

if __name__ == "__main__":
    run_taxonomy_viz()
