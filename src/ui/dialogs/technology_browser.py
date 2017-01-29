"""
    technology-browser.py

    Browses through the available game technologies.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.TXT for more details.
"""
from PySide.QtGui import QDialog
from PySide.QtGui import QFrame
from PySide.QtGui import QLabel
from PySide.QtGui import QBoxLayout
from PySide.QtGui import QPushButton
from PySide.QtGui import QComboBox
from PySide.QtGui import QCheckBox
from PySide.QtGui import QFont
from PySide.QtGui import QPixmap
from PySide.QtCore import Qt

from src.data import Language_Map
from src.data import Technologies
from src.model.technology import Part
from src.model.technology import ShipHull
from src.model.enumerations import TechnologyId
from src.model.enumerations import TechnologyCategory
from src.model.enumerations import TechnologyCategoryMapping
from src.model.enumerations import ResourcePaths
from src.model.enumerations import ResearchAreas
from src.model.enumerations import Minerals
from src.model.enumerations import ProductionCost


class TechnologyBrowser(QDialog):
    def __init__(self, player, parent=None):
        super(TechnologyBrowser, self).__init__(parent)

        self.selectedTechnologyIndex = 0

        self.init_user_controls()
        self.init_ui()
        self.bind_user_controls()
        self.player = player

    def init_user_controls(self):
        self.close_button = QPushButton(Language_Map["ui"]["general"]["close"])
        self.prev_button = QPushButton("<- {0}".format(
            Language_Map["ui"]["general"]["previous"]))

        self.next_button = QPushButton("{0} ->".format(
            Language_Map["ui"]["general"]["next"]))

        self.technology_categories = QComboBox()
        self.technology_categories.addItems(
            Language_Map["ui"]["technology-browser"]["technology-category-names"])

        self.show_available = QCheckBox(
            Language_Map["ui"]["technology-browser"]["show-available-option"])

        self.technology_label = QLabel("test")
        self.technology_image_label = QLabel("")

        self.ironium_cost = QLabel()
        self.boranium_cost = QLabel()
        self.germanium_cost = QLabel()
        self.resource_cost = QLabel()
        self.mass_value = QLabel()

        self.tech_requirements = []
        for i in xrange(ResearchAreas.Total):
            self.tech_requirements.append(QLabel())

        self.no_requirements = QLabel("<b>{0}</b>".format(
            Language_Map["tech-no-requirements"]))

        self.available_tech = QLabel("<b>{0}</b>".format(
            Language_Map["tech-available"]))

        self.research_cost = QLabel()

        self.technology_requirements_pane = QBoxLayout(QBoxLayout.TopToBottom)
        self.information_message = QLabel()
        self.information_message.setWordWrap(True)

        self.technology_fine_details_pane = QFrame()
        self.technology_fine_details_pane.setFrameStyle(QFrame.Panel | QFrame.Sunken)

    def bind_user_controls(self):
        self.close_button.clicked.connect(self.close_window)
        self.next_button.clicked.connect(self.next_technology)
        self.prev_button.clicked.connect(self.previous_technology)
        self.show_available.clicked.connect(self.show_available_technology)
        self.technology_categories.currentIndexChanged.connect(
            self.technology_category_change)

    def init_ui(self):
        self.setWindowTitle(
            Language_Map["ui"]["technology-browser"]["title"])

        self.setGeometry(200, 200, 525, 525)
        self.setFixedSize(525, 525)

        top_layout = QBoxLayout(QBoxLayout.LeftToRight)
        top_layout.addWidget(self.prev_button)
        top_layout.addWidget(self.technology_categories, 1)
        top_layout.addWidget(self.next_button)

        center_layout = QFrame()
        center_layout.setFrameStyle(QFrame.Panel | QFrame.Raised)

        frame_layout = QBoxLayout(QBoxLayout.TopToBottom)

        self.technology_label.setAlignment(Qt.AlignCenter)
        self.technology_label.setStyleSheet("QLabel { font: bold 14px; color: #000000 }")
        frame_layout.addWidget(self.technology_label)

        technology_overview_layout = QBoxLayout(QBoxLayout.LeftToRight)
        technology_overview_layout.addWidget(self.technology_image_label)

        mineral_label_layout = QBoxLayout(QBoxLayout.TopToBottom)
        ironium_label = QLabel("<b>{0}</b>".format(
            Language_Map["minerals"][Minerals.Ironium].title()))

        ironium_label.setStyleSheet("QLabel { color: #0000ff }")
        mineral_label_layout.addWidget(ironium_label)

        boranium_label = QLabel("<b>{0}</b>".format(
            Language_Map["minerals"][Minerals.Boranium].title()))
        boranium_label.setStyleSheet("QLabel { color: #008000 }")
        mineral_label_layout.addWidget(boranium_label)

        germanium_label = QLabel("<b>{0}</b>".format(
            Language_Map["minerals"][Minerals.Germanium].title()))
        germanium_label.setStyleSheet("QLabel { color: #ffff00 }")
        mineral_label_layout.addWidget(germanium_label)

        resources_label = QLabel("<b>{0}</b>".format(
            Language_Map["resources"].title()))
        resources_label.setStyleSheet("QLabel { color: #000000 }")
        mineral_label_layout.addWidget(resources_label)
        mineral_label_layout.addStretch(1)
        technology_overview_layout.addLayout(mineral_label_layout)

        mineral_value_layout = QBoxLayout(QBoxLayout.TopToBottom)
        mineral_value_layout.addWidget(self.ironium_cost)
        mineral_value_layout.addWidget(self.boranium_cost)
        mineral_value_layout.addWidget(self.germanium_cost)
        mineral_value_layout.addWidget(self.resource_cost)
        mineral_value_layout.addStretch(1)
        technology_overview_layout.addLayout(mineral_value_layout)

        technology_overview_layout.addStretch(1)

        mass_value_layout = QBoxLayout(QBoxLayout.TopToBottom)
        mass_value_layout.addWidget(self.mass_value)
        mass_value_layout.addStretch(1)
        technology_overview_layout.addLayout(mass_value_layout)

        technology_overview_layout.addStretch(1)

        frame_layout.addLayout(technology_overview_layout)

        technology_details_layout = QBoxLayout(QBoxLayout.LeftToRight)

        technology_requirements_layout = QBoxLayout(QBoxLayout.TopToBottom)
        req_label = QLabel(
            Language_Map["tech-requirements-title"])
        req_label.setStyleSheet("QLabel { color: #000000 }")

        font = QFont()
        font.setBold(True)
        req_label.setFont(font)

        technology_requirements_layout.addWidget(req_label)

        for i in xrange(ResearchAreas.Total):
            technology_requirements_layout.addWidget(self.tech_requirements[i])

        technology_requirements_layout.addWidget(self.no_requirements)
        technology_requirements_layout.addWidget(self.research_cost)
        technology_requirements_layout.addWidget(self.available_tech)
        technology_requirements_layout.addStretch(1)

        technology_requirements_layout.addLayout(
            self.technology_requirements_pane)
        technology_details_layout.addLayout(technology_requirements_layout)

        technology_details_layout.addWidget(self.technology_fine_details_pane, 1)

        frame_layout.addLayout(technology_details_layout, 1)

        technology_message_line = QFrame()
        technology_message_line.setFrameStyle(QFrame.HLine | QFrame.Sunken)
        frame_layout.addWidget(technology_message_line)

        self.information_message.setStyleSheet("QLabel { font: 10px; color: #000000 }")
        frame_layout.addWidget(self.information_message)

        center_layout.setLayout(frame_layout)

        bottom_layout = QBoxLayout(QBoxLayout.LeftToRight)
        bottom_layout.addWidget(self.show_available)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.close_button)

        main_layout = QBoxLayout(QBoxLayout.TopToBottom, self)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(center_layout, 1)
        main_layout.addLayout(bottom_layout)

        self.set_new_technology()

    def close_window(self):
        self.accept()

    def next_technology(self):
        selected_index = self.technology_categories.currentIndex()
        self.selectedTechnologyIndex = (
            (self.selectedTechnologyIndex + 1) % len(
                TechnologyCategoryMapping[selected_index]))

        self.set_new_technology()

    def previous_technology(self):
        selected_index = self.technology_categories.currentIndex()

        self.selectedTechnologyIndex = (
            (self.selectedTechnologyIndex - 1) % len(
                TechnologyCategoryMapping[selected_index]))

        self.set_new_technology()

    def show_available_technology(self):
        print "Show only available technology!"

    def set_new_technology(self):
        selected_index = self.technology_categories.currentIndex()

        tech_id = TechnologyCategoryMapping[selected_index][self.selectedTechnologyIndex]
        self.technology_label.setText(
            Language_Map["technology-names"][tech_id])

        tech_icon = "{0}/{1:03d}.png".format(
            ResourcePaths.TechnologyIcons, tech_id)

        self.technology_image_label.setPixmap(QPixmap(tech_icon))

        current_tech = Technologies[tech_id]

        self.ironium_cost.setText("{0!s}kT".format(
            current_tech.cost[ProductionCost.Ironium]))

        self.boranium_cost.setText("{0!s}kT".format(
            current_tech.cost[ProductionCost.Boranium]))

        self.germanium_cost.setText("{0!s}kT".format(
            current_tech.cost[ProductionCost.Germanium]))

        self.resource_cost.setText("{0!s}".format(
            current_tech.cost[ProductionCost.Resources]))

        if (isinstance(current_tech, Part) or
           isinstance(current_tech, ShipHull)):
            self.mass_value.setText("<b>Mass:</b> {0!s}kT".format(
                current_tech.mass))
        else:
            self.mass_value.setText("")

        self.set_technology_requirements(tech_id)
        self.set_technology_fine_details(tech_id)
        self.set_technology_message(tech_id)

    def set_technology_fine_details(self, tech_id):
        current_tech = Technologies[tech_id]
        fine_details_are_graphs = [
            TechnologyId.SDI,
            TechnologyId.MissileBattery,
            TechnologyId.LaserBattery,
            TechnologyId.PlanetaryShield,
            TechnologyId.NeutronShield,
            TechnologyId.SettlersDelight,
            TechnologyId.QuickJump5,
            TechnologyId.FuelMizer,
            TechnologyId.LongHump6,
            TechnologyId.DaddyLongLegs7,
            TechnologyId.AlphaDrive8,
            TechnologyId.TransGalacticDrive,
            TechnologyId.Interspace10,
            TechnologyId.TransStar10,
            TechnologyId.RadiatingHydroRamScoop,
            TechnologyId.SubGalacticFuelScoop,
            TechnologyId.TransGalacticFuelScoop,
            TechnologyId.TransGalacticSuperScoop,
            TechnologyId.TransGalacticMizerScoop,
            TechnologyId.GalaxyScoop
        ]

        if tech_id in fine_details_are_graphs:
            layout = QBoxLayout(QBoxLayout.TopToBottom)
            label = QLabel()
            label.setPixmap(QPixmap("{0}/graphs/{1:03d}.png".format(
                ResourcePaths.TechnologyIcons, tech_id)))

            layout.addWidget(label, 1)
            if self.technology_fine_details_pane.layout():
                dummy_widget = QLabel()
                old_layout = self.technology_fine_details_pane.layout()
                dummy_widget.setLayout(old_layout)

            self.technology_fine_details_pane.setLayout(layout)
        elif tech_id in TechnologyCategoryMapping[TechnologyCategory.Armor]:
            layout = QBoxLayout(QBoxLayout.TopToBottom)
            armor_strength = QLabel("<b>{0}:</b> {1!s}".format(
                Language_Map["ui"]["technology-browser"]["fine-details"]["armor-strength"],
                current_tech.armor_value))
            layout.addWidget(armor_strength)

            if tech_id == TechnologyId.FieldedKelarium:
                extra_label = QLabel(
                    Language_Map["ui"]["technology-browser"]["fine-details"]["fielded-kelarium"])

                extra_label.setWordWrap(True)
                layout.addWidget(extra_label)
            elif tech_id == TechnologyId.DepletedNeutronium:
                extra_label = QLabel(
                    Language_Map["ui"]["technology-browser"]["fine-details"]["depleted-neutronium"])
                extra_label.setWordWrap(True)
                layout.addWidget(extra_label)

            layout.addStretch(1)
            if self.technology_fine_details_pane.layout():
                dummy_widget = QLabel()
                old_layout = self.technology_fine_details_pane.layout()
                dummy_widget.setLayout(old_layout)

            self.technology_fine_details_pane.setLayout(layout)
        elif tech_id in TechnologyCategoryMapping[TechnologyCategory.BeamWeapons]:
            layout = QBoxLayout(QBoxLayout.TopToBottom)

            power = QLabel("<b>{0}:</b> {1!s}".format(
                Language_Map["ui"]["technology-browser"]["fine-details"]["power"],
                current_tech.power))
            layout.addWidget(power)

            range = QLabel("<b>{0}:</b> {1!s}".format(
                Language_Map["ui"]["technology-browser"]["fine-details"]["range"],
                current_tech.range))
            layout.addWidget(range)

            initiative = QLabel("<b>{0}:</b> {1!s}".format(
                Language_Map["ui"]["technology-browser"]["fine-details"]["initiative"],
                current_tech.initiative))
            layout.addWidget(initiative)

            if tech_id == TechnologyId.MiniGun:
                extra_label = QLabel(
                    Language_Map["ui"]["technology-browser"]["fine-details"]["mini-gun"])

                extra_label.setWordWrap(True)
                layout.addWidget(extra_label)
            elif (tech_id == TechnologyId.PulsedSapper or
                  tech_id == TechnologyId.PhasedSapper or
                  tech_id == TechnologyId.SyncroSapper):
                extra_label = QLabel(
                    Language_Map["ui"]["technology-browser"]["fine-details"]["sapper"])

                extra_label.setWordWrap(True)
                layout.addWidget(extra_label)
            elif tech_id == TechnologyId.GatlingGun:
                extra_label = QLabel(
                    Language_Map["ui"]["technology-browser"]["fine-details"]["gatling-gun"])

                extra_label.setWordWrap(True)
                layout.addWidget(extra_label)
            elif tech_id == TechnologyId.GatlingNeutrinoCannon:
                extra_label = QLabel(
                    Language_Map["ui"]["technology-browser"]["fine-details"]["gatling-neutrino-cannon"])

                extra_label.setWordWrap(True)
                layout.addWidget(extra_label)
            elif tech_id == TechnologyId.BigMuthaCannon:
                extra_label = QLabel(
                    Language_Map["ui"]["technology-browser"]["fine-details"]["big-mutha-cannon"])

                extra_label.setWordWrap(True)
                layout.addWidget(extra_label)

            layout.addStretch(1)
            if self.technology_fine_details_pane.layout():
                dummy_widget = QLabel()
                old_layout = self.technology_fine_details_pane.layout()
                dummy_widget.setLayout(old_layout)

            self.technology_fine_details_pane.setLayout(layout)

        elif tech_id in TechnologyCategoryMapping[TechnologyCategory.Bombs]:
            layout = QBoxLayout(QBoxLayout.TopToBottom)

            label = QLabel()
            label.setWordWrap(True)

            if tech_id == TechnologyId.RetroBomb:
                label.setText(Language_Map["ui"]["technology-browser"]["fine-details"]["retro-bomb"])
            elif current_tech.smart:
                label.setText(Language_Map["ui"]["technology-browser"]["fine-details"]["smart-bomb"].format(
                    current_tech.colonist_kill_percent,
                    current_tech.buildings_destroyed))
            else:
                if current_tech.minimum_colonists_killed > 0:
                    label.setText(Language_Map["ui"]["technology-browser"]["fine-details"]["normal-bomb-with-minimum"].format(
                        current_tech.colonist_kill_percent,
                        current_tech.minimum_colonists_killed,
                        current_tech.buildings_destroyed))
                else:
                    label.setText(Language_Map["ui"]["technology-browser"]["fine-details"]["normal-bomb-no-minimum"].format(
                        current_tech.colonist_kill_percent,
                        current_tech.buildings_destroyed))

            layout.addWidget(label)

            layout.addStretch(1)
            if self.technology_fine_details_pane.layout():
                dummy_widget = QLabel()
                old_layout = self.technology_fine_details_pane.layout()
                dummy_widget.setLayout(old_layout)

            self.technology_fine_details_pane.setLayout(layout)





    def set_technology_message(self, tech_id):
        planetary_scanners_and_defenses = [
            TechnologyId.Viewer50,
            TechnologyId.Viewer90,
            TechnologyId.Scoper150,
            TechnologyId.Scoper220,
            TechnologyId.Scoper280,
            TechnologyId.SDI,
            TechnologyId.MissileBattery
       ]

        penetrating_scanners = [
            TechnologyId.Snooper320X,
            TechnologyId.Snooper400X,
            TechnologyId.Snooper500X,
            TechnologyId.Snooper620X,
            TechnologyId.FerretScanner,
            TechnologyId.DolphinScanner,
            TechnologyId.ElephantScanner
        ]

        advanced_defenses = [
            TechnologyId.LaserBattery,
            TechnologyId.PlanetaryShield,
            TechnologyId.NeutronShield
        ]

        war_monger_parts = [
            TechnologyId.GatlingNeutrinoCannon,
            TechnologyId.Blunderbuss
        ]

        smart_bombs = [
            TechnologyId.SmartBomb,
            TechnologyId.NeutronBomb,
            TechnologyId.EnrichedNeutronBomb,
            TechnologyId.PeerlessBomb,
            TechnologyId.AnnihilatorBomb
        ]

        ram_scoop_engines = [
            TechnologyId.SubGalacticFuelScoop,
            TechnologyId.TransGalacticFuelScoop,
            TechnologyId.TransGalacticSuperScoop,
            TechnologyId.TransGalacticMizerScoop,
            TechnologyId.GalaxyScoop
        ]

        sd_mines = [
            TechnologyId.MineDispenser40,
            TechnologyId.MineDispenser80,
            TechnologyId.MineDispenser130,
            TechnologyId.HeavyDispenser50,
            TechnologyId.HeavyDispenser110,
            TechnologyId.HeavyDispenser200,
            TechnologyId.SpeedTrap30,
            TechnologyId.SpeedTrap50
        ]

        arm_miners = [
            TechnologyId.RoboMidgetMiner,
            TechnologyId.RoboUltraMiner
        ]

        normal_miners = [
            TechnologyId.RoboMiner,
            TechnologyId.RoboMaxiMiner,
            TechnologyId.RoboSuperMiner
        ]

        normal_gates = [
            TechnologyId.Stargate100_250,
            TechnologyId.Stargate150_600,
            TechnologyId.Stargate300_500
        ]

        it_gates = [
            TechnologyId.StargateAny_300,
            TechnologyId.Stargate100_Any,
            TechnologyId.StargateAny_800,
            TechnologyId.StargateAny_Any
        ]

        pp_mass_drivers = [
            TechnologyId.MassDriver5,
            TechnologyId.MassDriver6,
            TechnologyId.SuperDriver8,
            TechnologyId.SuperDriver9,
            TechnologyId.UltraDriver11,
            TechnologyId.UltraDriver12,
            TechnologyId.UltraDriver13
        ]

        tt_tech = [
            TechnologyId.TotalTerraform3,
            TechnologyId.TotalTerraform5,
            TechnologyId.TotalTerraform7,
            TechnologyId.TotalTerraform10,
            TechnologyId.TotalTerraform15,
            TechnologyId.TotalTerraform20,
            TechnologyId.TotalTerraform25,
            TechnologyId.TotalTerraform30
        ]

        missiles = [
            TechnologyId.JihadMissile,
            TechnologyId.JuggernautMissile,
            TechnologyId.DoomsdayMissile,
            TechnologyId.ArmageddonMissile
        ]

        if tech_id in planetary_scanners_and_defenses:
            self.information_message.setText(
                Language_Map["scanner-defense-AR-restriction"])
        elif tech_id in penetrating_scanners:
            self.information_message.setText(
                Language_Map["penetrating-scanner-restriction"])
        elif tech_id in advanced_defenses:
            self.information_message.setText(
                Language_Map["advanced-defenses-restriction"])
        elif tech_id == TechnologyId.FieldedKelarium:
            self.information_message.setText(
                Language_Map["inner-strength-armor"])
        elif tech_id == TechnologyId.DepletedNeutronium:
            self.information_message.setText(
                Language_Map["super-stealth-armor"])
        elif tech_id == TechnologyId.MiniGun:
            self.information_message.setText(
                Language_Map["inner-strength-part"])
        elif tech_id in war_monger_parts:
            self.information_message.setText(
                Language_Map["war-monger-part"])
        elif tech_id == TechnologyId.RetroBomb:
            self.information_message.setText(
                Language_Map["claim-adjuster-part"])
        elif tech_id == TechnologyId.TransportCloaking or tech_id == TechnologyId.UltraStealthCloak:
            self.information_message.setText(
                Language_Map["super-stealth-cloak"])
        elif tech_id == TechnologyId.Jammer10 or tech_id == TechnologyId.Jammer50:
            self.information_message.setText(
                Language_Map["inner-strength-jammer"])
        elif tech_id == TechnologyId.FluxCapacitor:
            self.information_message.setText(
                Language_Map["hyper-expansion-device"])
        elif tech_id in smart_bombs:
            self.information_message.setText(
                Language_Map["inner-strength-smart-bomb-restriction"])
        elif tech_id == TechnologyId.EnergyDampener:
            self.information_message.setText(
                Language_Map["space-demolition-device"])
        elif tech_id == TechnologyId.TachyonDetector:
            self.information_message.setText(
                Language_Map["inner-strength-device"])
        elif tech_id == TechnologyId.AntiMatterGenerator:
            self.information_message.setText(
                Language_Map["interstellar-traveler-device"])
        elif tech_id == TechnologyId.SettlersDelight:
            self.information_message.setText(
                Language_Map["settlers-delight-engine"])
        elif tech_id == TechnologyId.FuelMizer:
            self.information_message.setText(
                Language_Map["ife-engine"])
        elif tech_id == TechnologyId.Interspace10:
            self.information_message.setText(
                Language_Map["no-ram-scoop-engine"])
        elif tech_id == TechnologyId.RadiatingHydroRamScoop:
            self.information_message.setText(
                Language_Map["radiating-engine"])
        elif tech_id in ram_scoop_engines:
            self.information_message.setText(
                Language_Map["no-ram-scoop-engine-restriction"])
        elif tech_id == TechnologyId.ColonizationModule:
            self.information_message.setText(
                Language_Map["colonization-module-restriction"])
        elif tech_id == TechnologyId.OrbitalConstructionModule:
            self.information_message.setText(
                Language_Map["ar-only-part"])
        elif tech_id in sd_mines:
            self.information_message.setText(
                Language_Map["sd-mine"])
        elif tech_id == TechnologyId.MineDispenser50:
            self.information_message.setText(
                Language_Map["war-monger-restriction"])
        elif tech_id == TechnologyId.SpeedTrap20:
            self.information_message.setText(
                Language_Map["speed-trap-20"])
        elif tech_id in arm_miners:
            self.information_message.setText(
                Language_Map["arm-robot"])
        elif tech_id in normal_miners:
            self.information_message.setText(
                Language_Map["obrm-restriction"])
        elif tech_id == TechnologyId.OrbitalAdjuster:
            self.information_message.setText(
                Language_Map["claim-adjuster-part"])
        elif tech_id in normal_gates:
            self.information_message.setText(
                Language_Map["hyper-expansion-restriction"])
        elif tech_id in it_gates:
            self.information_message.setText(
                Language_Map["it-stargate"])
        elif tech_id in pp_mass_drivers:
            self.information_message.setText(
                Language_Map["pp-mass-driver"])
        elif (tech_id == TechnologyId.PickPocketScanner or
              tech_id == TechnologyId.ChameleonScanner or
              tech_id == TechnologyId.RobberBaronScanner):
            self.information_message.setText(
                Language_Map["super-stealth-scanner"])
        elif tech_id == TechnologyId.CrobySharmor:
            self.information_message.setText(
                Language_Map["inner-strength-shield"])
        elif tech_id == TechnologyId.ShadowShield:
            self.information_message.setText(
                Language_Map["super-stealth-shield"])
        elif (tech_id == TechnologyId.SuperFreighter or
              tech_id == TechnologyId.FuelTransport):
            self.information_message.setText(
                Language_Map["inner-strength-hull"])
        elif (tech_id == TechnologyId.Scout or
              tech_id == TechnologyId.Frigate or
              tech_id == TechnologyId.Destroyer):
            self.information_message.setText(
                Language_Map["joat-hull"])
        elif (tech_id == TechnologyId.BattleCruiser or
              tech_id == TechnologyId.Dreadnought):
            self.information_message.setText(
                Language_Map["war-monger-hull"])
        elif (tech_id == TechnologyId.Rogue or
              tech_id == TechnologyId.StealthBomber):
            self.information_message.setText(
                Language_Map["super-stealth-hull"])
        elif (tech_id == TechnologyId.MiniColonyShip or
              tech_id == TechnologyId.MetaMorph):
            self.information_message.setText(
                Language_Map["hyper-expansion-hull"])
        elif (tech_id == TechnologyId.MidgetMiner or
              tech_id == TechnologyId.Miner or
              tech_id == TechnologyId.UltraMiner):
            self.information_message.setText(
                Language_Map["arm-hull"])
        elif tech_id == TechnologyId.MaxiMiner:
            self.information_message.setText(
                Language_Map["obrm-hull-restriction"])
        elif (tech_id == TechnologyId.MiniMineLayer or
              tech_id == TechnologyId.SuperMineLayer):
            self.information_message.setText(
                Language_Map["sd-hull"])
        elif (tech_id == TechnologyId.SpaceDock or
              tech_id == TechnologyId.UltraStation):
            self.information_message.setText(
                Language_Map["improved-starbases-hull"])
        elif tech_id == TechnologyId.DeathStar:
            self.information_message.setText(
                Language_Map["ar-starbase-hull"])
        elif tech_id in tt_tech:
            self.information_message.setText(
                Language_Map["total-terraforming-tech"])
        elif tech_id in missiles:
            self.information_message.setText(
                Language_Map["capital-ship-missiles"])
        else:
            self.information_message.setText("")

    def set_technology_requirements(self, tech_id):
        current_tech = Technologies[tech_id]

        has_req = False

        for i in xrange(ResearchAreas.Total):
            if current_tech.requirements[i] > 0:
                self.tech_requirements[i].setVisible(True)
                self.tech_requirements[i].setText("<b>{0}:</b> {1!s}".format(
                    Language_Map["tech-abbreviations"][i],
                    current_tech.requirements[i]))

                has_req = True
            else:
                self.tech_requirements[i].setVisible(False)

        self.no_requirements.setVisible(not has_req)

        # TODO: logic for tech available vs. cost to obtain

    def technology_category_change(self):
        self.selectedTechnologyIndex = 0
        self.set_new_technology()
