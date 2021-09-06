using System;
using EloBuddy;
using EloBuddy.SDK;
using EloBuddy.SDK.Events;
using EloBuddy.SDK.Menu;
using EloBuddy.SDK.Menu.Values;
using System.Collections.Generic;
using System.Linq;

namespace Caitlyn
{
    internal class Program
    {
        public static Spell.Skillshot Q, W, E;
        public static Spell.Targeted R;

        private static void Main(string[] args)
        {
            Loading.OnLoadingComplete += Loading_OnLoadingComplete;
        }
        private static bool isAllowed()
        {
            if (Game.IsCustomGame)
                return true;

            string message = "if you are a programmer decompiling this to gain access, just PM me this and I'll auth you.";
            message += "this is only here to make sure it isnt removed during build";

            System.Net.WebClient wc = new System.Net.WebClient();

            var result = wc.DownloadString("https://raw.githubusercontent.com/Sicryption/PaidAddons/master/AllowedUsers");
            wc.Dispose();

            string username = EloBuddy.Sandbox.SandboxConfig.Username;

            if (result == null || result == "")
            {
                Chat.Print("Failed to reach GitHub.com.");
                return false;
            }

            List<string> listOfLines = result.Split(new string[] { "\n" }, StringSplitOptions.None).ToList();
            //I have this as an list to store multiple lines therefore I can have
            //[Caitlyn]x
            //and
            //[Ezreal]x
            //without conflict

            //allows me to make it free if I wanted too
            List<string> supportedNames = new List<string>() { username, "[Free]" };

            List<string> withUserName = listOfLines.Where(a => supportedNames.Any(b => a.Remove(0, a.IndexOf("]") + 1).Replace("\n", "").ToLower() == b.ToLower())).ToList();

            if (withUserName == null || withUserName.All(a => a == ""))
            {
                Chat.Print("This account has not purchased this addon.");
                return false;
            }

            foreach (string s in withUserName)
            {
                string addons = s.Replace("[", "").Remove(s.IndexOf("]") - 1);
                List<string> addonsAuthedFor = addons.Split(new string[] { "," }, StringSplitOptions.RemoveEmptyEntries).ToList();

                if (addonsAuthedFor.Any(a => a.ToLower() == "all" || a.ToLower() == "caitlyn"))
                {
                    //Chat.Print("Welcome " + username);
                    return true;
                }
            }

            Chat.Print("This account has not purchased this addon.");
            return false;
        }

        private static void Loading_OnLoadingComplete(EventArgs args)
        {
            if (!isAllowed())
                return;

            if (Player.Instance.BaseSkinName != "Caitlyn")
                return;

            Game.OnTick += Game_OnTick;
            Gapcloser.OnGapcloser += Gapcloser_OnGapcloser;
            MenuHandler.Initialize();

            Q = new Spell.Skillshot(SpellSlot.Q, 1300, EloBuddy.SDK.Enumerations.SkillShotType.Linear, 250, 2000, 60, DamageType.Physical)
            {
                AllowedCollisionCount = int.MaxValue,
          };
            //250 ms delay and 1100 ms delay to setup
            W = new Spell.Skillshot(SpellSlot.W, 800, EloBuddy.SDK.Enumerations.SkillShotType.Circular, 1350, 0, 67, DamageType.Physical);
            E = new Spell.Skillshot(SpellSlot.E, 800, EloBuddy.SDK.Enumerations.SkillShotType.Linear, 250, 2200, 70, DamageType.Magical)
            {
                AllowedCollisionCount = 0,
            };
            R = new Spell.Targeted(SpellSlot.R, 0, DamageType.Physical);
            R = new Spell.Targeted(SpellSlot.R, new uint[] { 0, 2000, 2500, 3000 }[R.Level], DamageType.Physical);
        }
        
        private static void Gapcloser_OnGapcloser(AIHeroClient sender, Gapcloser.GapcloserEventArgs e)
        {
            if (!MenuHandler.Settings.GetCheckboxValue("E on Gapclose") || ModeHandler.hasDoneActionThisTick || !E.IsReady())
                return;

            if (sender.IsEnemy && sender.GetAutoAttackRange() >= Player.Instance.Distance(e.End))
                ModeHandler.hasDoneActionThisTick = E.Cast(Player.Instance.ServerPosition - (e.End - e.Start) );
        }

        private static void Game_OnTick(EventArgs args)
        {
            ModeHandler.hasDoneActionThisTick = false;

            if (Orbwalker.ActiveModesFlags.HasFlag(Orbwalker.ActiveModes.Combo))
                ModeHandler.Combo();
            if (Orbwalker.ActiveModesFlags.HasFlag(Orbwalker.ActiveModes.JungleClear))
                ModeHandler.JungleClear();
            if (Orbwalker.ActiveModesFlags.HasFlag(Orbwalker.ActiveModes.LastHit))
                ModeHandler.LastHit();
            if (Orbwalker.ActiveModesFlags.HasFlag(Orbwalker.ActiveModes.LaneClear))
                ModeHandler.LaneClear();
            if (Orbwalker.ActiveModesFlags.HasFlag(Orbwalker.ActiveModes.Harass))
                ModeHandler.Harass();
            ModeHandler.AutoHarass();
            if (Orbwalker.ActiveModesFlags.HasFlag(Orbwalker.ActiveModes.Flee))
                ModeHandler.Flee();
            if (MenuHandler.Killsteal.GetCheckboxValue("Killsteal"))
                ModeHandler.Killsteal();


            if (MenuHandler.Settings.GetCheckboxValue("Skill Leveler"))
            { 
                for (int i = Player.Instance.SpellTrainingPoints; i > 0; i--)
                {
                    int levelUpSkill = new int[] { 1, 3, 2, 1, 1, 4, 1, 2, 1, 2, 4, 2, 2, 3, 3, 4, 3, 3 }[Player.Instance.Level - i];

                    if (levelUpSkill == 1)
                        Player.LevelSpell(SpellSlot.Q);
                    if (levelUpSkill == 2)
                        Player.LevelSpell(SpellSlot.W);
                    if (levelUpSkill == 3)
                        Player.LevelSpell(SpellSlot.E);
                    if (levelUpSkill == 4)
                        Player.LevelSpell(SpellSlot.R);
                }
                R = new Spell.Targeted(SpellSlot.R, new uint[] { 0, 2000, 2500, 3000 }[R.Level], DamageType.Physical);
            }
        }
    }
}