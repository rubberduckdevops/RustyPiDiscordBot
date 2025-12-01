import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import Button, View
import os
from dotenv import load_dotenv
import asyncio
from datetime import time as dt_time
from database import Database

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Initialize database
db = None

# Button view for voting
class VoteView(View):
    def __init__(self, question_id: int):
        super().__init__(timeout=None)
        self.question_id = question_id

    @discord.ui.button(label="Option A", style=discord.ButtonStyle.primary, emoji="👈")
    async def vote_a(self, interaction: discord.Interaction, button: Button):
        await self.process_vote(interaction, 'a')

    @discord.ui.button(label="Option B", style=discord.ButtonStyle.primary, emoji="👉")
    async def vote_b(self, interaction: discord.Interaction, button: Button):
        await self.process_vote(interaction, 'b')

    async def process_vote(self, interaction: discord.Interaction, choice: str):
        # Check if user already voted on this question
        has_voted = await db.has_user_voted(interaction.user.id, self.question_id)

        if has_voted:
            await interaction.response.send_message("You've already voted on this question! 🗳️", ephemeral=True)
            return

        # Record the vote
        await db.record_vote(interaction.user.id, self.question_id, choice)

        # Award coins for voting
        await db.award_coins(interaction.user.id, 10)

        # Update streak
        await db.update_streak(interaction.user.id)

        # Get updated results
        results = await db.get_question_results(self.question_id)
        total_votes = results['a_votes'] + results['b_votes']

        # Get question details
        question_data = await db.get_question_by_id(self.question_id)
        _, question, option_a, option_b, category = question_data

        # Create results embed to show the user
        user_embed = discord.Embed(
            title="Thanks for voting!",
            description=f"You chose **{'Option A' if choice == 'a' else 'Option B'}**",
            color=discord.Color.green()
        )

        a_percent = (results['a_votes'] / total_votes) * 100 if total_votes > 0 else 0
        b_percent = (results['b_votes'] / total_votes) * 100 if total_votes > 0 else 0

        user_embed.add_field(
            name="Current Results",
            value=f"👈 Option A: {a_percent:.1f}% ({results['a_votes']} votes)\n"
                  f"👉 Option B: {b_percent:.1f}% ({results['b_votes']} votes)",
            inline=False
        )

        user_embed.add_field(
            name="Reward",
            value=f"You earned 10 coins! 🪙",
            inline=False
        )

        # Send ephemeral response to voter
        await interaction.response.send_message(embed=user_embed, ephemeral=True)

        # Update the original message with current vote counts
        original_embed = discord.Embed(
            title="Would You Rather?",
            description=question,
            color=discord.Color.blue()
        )

        if category:
            original_embed.set_footer(text=f"Category: {category} | Total Votes: {total_votes}")

        original_embed.add_field(name="👈 Option A", value=option_a, inline=False)
        original_embed.add_field(name="👉 Option B", value=option_b, inline=False)
        original_embed.add_field(
            name="Live Results",
            value=f"👈 {a_percent:.1f}% ({results['a_votes']} votes)\n"
                  f"👉 {b_percent:.1f}% ({results['b_votes']} votes)",
            inline=False
        )

        # Update the message to show live results, keep buttons active
        try:
            await interaction.message.edit(embed=original_embed, view=self)
        except:
            pass  # Message might have been deleted

# Daily question task
@tasks.loop(time=dt_time(hour=12, minute=0))  # Runs at 12:00 PM UTC daily
async def post_daily_question():
    """Post a daily Would You Rather question to configured channels"""
    if db is None:
        return

    # Get all guilds with daily questions enabled
    daily_configs = await db.get_all_daily_channels()

    for guild_id, channel_id in daily_configs:
        try:
            channel = bot.get_channel(channel_id)
            if channel is None:
                continue

            # Get a random question
            question_data = await db.get_random_question()
            if not question_data:
                continue

            question_id, question, option_a, option_b, category = question_data

            # Create embed
            embed = discord.Embed(
                title="📅 Daily Would You Rather Question!",
                description=question,
                color=discord.Color.gold()
            )

            if category:
                embed.set_footer(text=f"Category: {category} | Daily Question")

            embed.add_field(name="👈 Option A", value=option_a, inline=False)
            embed.add_field(name="👉 Option B", value=option_b, inline=False)
            embed.add_field(name="Vote to Earn Coins!", value="Click a button below to vote and earn 10 coins!", inline=False)

            # Create voting buttons
            view = VoteView(question_id)

            # Post to channel
            await channel.send("@here It's time for the daily Would You Rather! 🎲", embed=embed, view=view)
            print(f"Posted daily question to {channel.guild.name} - #{channel.name}")

        except Exception as e:
            print(f"Error posting daily question to guild {guild_id}: {e}")

@bot.event
async def on_ready():
    """Event triggered when bot successfully connects to Discord"""
    global db
    db = Database('wyr_bot.db')
    await db.initialize()

    # Sync slash commands to all guilds (faster than global sync)
    try:
        # Sync to each guild for instant updates
        for guild in bot.guilds:
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"Synced {len(synced)} command(s) to {guild.name}")

        # Also sync globally (takes up to 1 hour to propagate)
        synced_global = await bot.tree.sync()
        print(f"Synced {len(synced_global)} command(s) globally")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    # Start daily question task
    if not post_daily_question.is_running():
        post_daily_question.start()
        print("Daily question task started!")

    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

@bot.tree.command(name='ping', description='Check bot latency')
async def ping(interaction: discord.Interaction):
    """Test command to check if bot is responsive"""
    print(f'Pong! 🏓 Latency: {round(bot.latency * 1000)}ms')
    await interaction.response.send_message(f'Pong! 🏓 Latency: {round(bot.latency * 1000)}ms')

@bot.tree.command(name='wyr', description='Get a random Would You Rather question')
async def would_you_rather(interaction: discord.Interaction):
    """Display a random Would You Rather question"""
    question_data = await db.get_random_question()

    if not question_data:
        await interaction.response.send_message("No questions available yet! Add some questions first.")
        return

    question_id, question, option_a, option_b, category = question_data

    # Check if user already voted on this question
    has_voted = await db.has_user_voted(interaction.user.id, question_id)

    # Create embed for the question
    embed = discord.Embed(
        title="Would You Rather?",
        description=question,
        color=discord.Color.blue()
    )

    if category:
        embed.set_footer(text=f"Category: {category}")

    embed.add_field(name="👈 Option A", value=option_a, inline=False)
    embed.add_field(name="👉 Option B", value=option_b, inline=False)

    # Always show buttons - the VoteView will handle if someone already voted
    view = VoteView(question_id)

    # If user already voted, show them the results in the embed
    if has_voted:
        results = await db.get_question_results(question_id)
        total_votes = results['a_votes'] + results['b_votes']

        if total_votes > 0:
            a_percent = (results['a_votes'] / total_votes) * 100
            b_percent = (results['b_votes'] / total_votes) * 100
            embed.add_field(
                name="Current Results",
                value=f"👈 {a_percent:.1f}% ({results['a_votes']} votes)\n"
                      f"👉 {b_percent:.1f}% ({results['b_votes']} votes)",
                inline=False
            )
            embed.set_footer(text=f"Category: {category} | You've already voted on this question" if category else "You've already voted on this question")

    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name='balance', description='Check your coin balance and streak')
async def balance(interaction: discord.Interaction):
    """Check your coin balance and streak"""
    user_data = await db.get_user(interaction.user.id)

    embed = discord.Embed(
        title=f"{interaction.user.name}'s Balance",
        color=discord.Color.gold()
    )

    embed.add_field(name="Coins", value=f"🪙 {user_data['coins']}", inline=True)
    embed.add_field(name="Streak", value=f"🔥 {user_data['streak']} days", inline=True)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='leaderboard', description='View the top 10 users by coins')
async def leaderboard(interaction: discord.Interaction):
    """Show the top users by coins"""
    top_users = await db.get_leaderboard(10)

    if not top_users:
        await interaction.response.send_message("No users on the leaderboard yet!")
        return

    embed = discord.Embed(
        title="Leaderboard - Top 10",
        color=discord.Color.purple()
    )

    description = ""
    for i, (user_id, coins, streak) in enumerate(top_users, 1):
        try:
            user = await bot.fetch_user(user_id)
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            description += f"{medal} **{user.name}** - 🪙 {coins} (🔥 {streak})\n"
        except:
            # Skip users that can't be fetched
            continue

    embed.description = description
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='addquestion', description='Add a new Would You Rather question (Admin only)')
@app_commands.describe(
    question='The main question text',
    option_a='First option',
    option_b='Second option',
    category='Question category (optional)'
)
async def add_question(
    interaction: discord.Interaction,
    question: str,
    option_a: str,
    option_b: str,
    category: str = "General"
):
    """Add a new Would You Rather question (Admin only)"""
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command!", ephemeral=True)
        return

    try:
        await db.add_question(question, option_a, option_b, category)
        await interaction.response.send_message(f"✅ Question added successfully!\n**Category:** {category}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error adding question: {str(e)}", ephemeral=True)

# Approval button view
class ApprovalView(View):
    def __init__(self, submission_id: int, submitter_id: int):
        super().__init__(timeout=None)
        self.submission_id = submission_id
        self.submitter_id = submitter_id

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success, emoji="✅")
    async def approve(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Only administrators can approve questions!", ephemeral=True)
            return

        success = await db.approve_submission(self.submission_id, interaction.user.id)

        if success:
            # Notify submitter
            try:
                submitter = await bot.fetch_user(self.submitter_id)
                await submitter.send(f"✅ Your question submission (ID: {self.submission_id}) has been approved!")
            except:
                pass

            # Update the embed to show approval
            embed = interaction.message.embeds[0]
            embed.color = discord.Color.green()
            embed.title = "✅ APPROVED - Question Submission"

            # Edit via the interaction response (works with ephemeral messages)
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            await interaction.response.send_message("❌ Failed to approve submission.", ephemeral=True)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger, emoji="❌")
    async def reject(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Only administrators can reject questions!", ephemeral=True)
            return

        await db.reject_submission(self.submission_id, interaction.user.id)

        # Notify submitter
        try:
            submitter = await bot.fetch_user(self.submitter_id)
            await submitter.send(f"❌ Your question submission (ID: {self.submission_id}) has been rejected.")
        except:
            pass

        # Update the embed to show rejection
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.title = "❌ REJECTED - Question Submission"

        # Edit via the interaction response (works with ephemeral messages)
        await interaction.response.edit_message(embed=embed, view=None)

@bot.tree.command(name='submit', description='Submit a Would You Rather question for approval')
@app_commands.describe(
    question='The main question text',
    option_a='First option',
    option_b='Second option',
    category='Question category (optional)'
)
async def submit_question(
    interaction: discord.Interaction,
    question: str,
    option_a: str,
    option_b: str,
    category: str = "General"
):
    """Submit a Would You Rather question for admin approval"""
    try:
        await db.submit_question(interaction.user.id, question, option_a, option_b, category)

        embed = discord.Embed(
            title="Question Submitted! 📝",
            description="Your question has been submitted for admin approval.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="👈 Option A", value=option_a, inline=True)
        embed.add_field(name="👉 Option B", value=option_b, inline=True)
        embed.add_field(name="Category", value=category, inline=False)
        embed.set_footer(text="You'll receive a DM when your question is reviewed!")

        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error submitting question: {str(e)}", ephemeral=True)

@bot.tree.command(name='pending', description='View pending question submissions (Admin only)')
async def view_pending(interaction: discord.Interaction):
    """View pending question submissions"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Only administrators can view pending submissions!", ephemeral=True)
        return

    submissions = await db.get_pending_submissions(5)  # Show 5 at a time

    if not submissions:
        await interaction.response.send_message("No pending submissions! 🎉", ephemeral=True)
        return

    # Send defer since we might send multiple messages
    await interaction.response.defer(ephemeral=True)

    for submission in submissions:
        sub_id, submitter_id, question, option_a, option_b, category, submitted_at = submission

        try:
            submitter = await bot.fetch_user(submitter_id)
            submitter_name = submitter.name
        except:
            submitter_name = f"Unknown User (ID: {submitter_id})"

        embed = discord.Embed(
            title="Question Submission for Review",
            description=question,
            color=discord.Color.gold()
        )
        embed.add_field(name="👈 Option A", value=option_a, inline=True)
        embed.add_field(name="👉 Option B", value=option_b, inline=True)
        embed.add_field(name="Category", value=category, inline=False)
        embed.add_field(name="Submitted By", value=submitter_name, inline=True)
        embed.add_field(name="Submission ID", value=str(sub_id), inline=True)
        embed.set_footer(text=f"Submitted at: {submitted_at}")

        view = ApprovalView(sub_id, submitter_id)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name='mysubmissions', description='View your submitted questions')
async def my_submissions(interaction: discord.Interaction):
    """View your submitted questions"""
    submissions = await db.get_user_submissions(interaction.user.id)

    if not submissions:
        await interaction.response.send_message("You haven't submitted any questions yet! Use `/submit` to submit one.", ephemeral=True)
        return

    embed = discord.Embed(
        title="Your Submitted Questions",
        color=discord.Color.blue()
    )

    for sub_id, question, option_a, option_b, category, status, submitted_at in submissions[:10]:
        status_emoji = "⏳" if status == "pending" else "✅" if status == "approved" else "❌"
        embed.add_field(
            name=f"{status_emoji} ID: {sub_id} - {status.upper()}",
            value=f"**Q:** {question[:100]}...\n**Category:** {category}",
            inline=False
        )

    embed.set_footer(text=f"Showing {min(len(submissions), 10)} of {len(submissions)} submissions")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name='setdaily', description='Set up daily questions (Admin only)')
@app_commands.describe(channel='The channel where daily questions will be posted')
async def set_daily(interaction: discord.Interaction, channel: discord.TextChannel):
    """Set the channel for daily Would You Rather questions"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Only administrators can configure daily questions!", ephemeral=True)
        return

    try:
        await db.set_daily_channel(interaction.guild.id, channel.id)

        embed = discord.Embed(
            title="✅ Daily Questions Enabled!",
            description=f"Daily Would You Rather questions will be posted to {channel.mention} every day at 12:00 PM UTC.",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Next Question",
            value="The next question will post at the scheduled time tomorrow!",
            inline=False
        )
        embed.add_field(
            name="Test It Now",
            value="Use `/testdaily` to post a test question immediately.",
            inline=False
        )

        await interaction.response.send_message(embed=embed)
        print(f"Daily questions enabled for {interaction.guild.name} in #{channel.name}")

    except Exception as e:
        await interaction.response.send_message(f"❌ Error setting up daily questions: {str(e)}", ephemeral=True)

@bot.tree.command(name='disabledaily', description='Disable daily questions (Admin only)')
async def disable_daily(interaction: discord.Interaction):
    """Disable daily Would You Rather questions"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Only administrators can configure daily questions!", ephemeral=True)
        return

    try:
        await db.disable_daily_questions(interaction.guild.id)

        embed = discord.Embed(
            title="Daily Questions Disabled",
            description="Daily Would You Rather questions have been disabled for this server.",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed)
        print(f"Daily questions disabled for {interaction.guild.name}")

    except Exception as e:
        await interaction.response.send_message(f"❌ Error disabling daily questions: {str(e)}", ephemeral=True)

@bot.tree.command(name='testdaily', description='Post a daily question now (Admin only)')
async def test_daily(interaction: discord.Interaction):
    """Test the daily question feature by posting one immediately"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Only administrators can test daily questions!", ephemeral=True)
        return

    # Get the daily channel config
    config = await db.get_daily_channel(interaction.guild.id)

    if not config or not config['enabled']:
        await interaction.response.send_message("❌ Daily questions are not enabled! Use `/setdaily` first.", ephemeral=True)
        return

    try:
        channel = bot.get_channel(config['channel_id'])
        if channel is None:
            await interaction.response.send_message("❌ Configured channel not found!", ephemeral=True)
            return

        # Get a random question
        question_data = await db.get_random_question()
        if not question_data:
            await interaction.response.send_message("❌ No questions available!", ephemeral=True)
            return

        question_id, question, option_a, option_b, category = question_data

        # Create embed
        embed = discord.Embed(
            title="📅 Daily Would You Rather Question! (TEST)",
            description=question,
            color=discord.Color.gold()
        )

        if category:
            embed.set_footer(text=f"Category: {category} | Daily Question Test")

        embed.add_field(name="👈 Option A", value=option_a, inline=False)
        embed.add_field(name="👉 Option B", value=option_b, inline=False)
        embed.add_field(name="Vote to Earn Coins!", value="Click a button below to vote and earn 10 coins!", inline=False)

        # Create voting buttons
        view = VoteView(question_id)

        # Post to channel
        await channel.send("@here It's time for the daily Would You Rather! 🎲 (This is a test)", embed=embed, view=view)
        await interaction.response.send_message(f"✅ Test question posted to {channel.mention}!", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"❌ Error posting test question: {str(e)}", ephemeral=True)

@bot.tree.command(name='help', description='Show all available commands')
async def help_command(interaction: discord.Interaction):
    """Show all available commands"""
    embed = discord.Embed(
        title="Would You Rather Bot - Commands",
        description="Here are all the available commands:",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="/wyr",
        value="Get a random Would You Rather question",
        inline=False
    )
    embed.add_field(
        name="/balance",
        value="Check your coin balance and streak",
        inline=False
    )
    embed.add_field(
        name="/leaderboard",
        value="View the top 10 users by coins",
        inline=False
    )
    embed.add_field(
        name="/ping",
        value="Check bot latency",
        inline=False
    )
    embed.add_field(
        name="/submit",
        value="Submit a Would You Rather question for admin approval",
        inline=False
    )
    embed.add_field(
        name="/mysubmissions",
        value="View the status of your submitted questions",
        inline=False
    )
    embed.add_field(
        name="/addquestion (Admin only)",
        value="Add a new question directly (bypasses approval)",
        inline=False
    )
    embed.add_field(
        name="/pending (Admin only)",
        value="View and approve/reject pending question submissions",
        inline=False
    )
    embed.add_field(
        name="/setdaily (Admin only)",
        value="Enable daily questions in a specific channel",
        inline=False
    )
    embed.add_field(
        name="/disabledaily (Admin only)",
        value="Disable daily questions",
        inline=False
    )
    embed.add_field(
        name="/testdaily (Admin only)",
        value="Post a test daily question immediately",
        inline=False
    )

    embed.set_footer(text="Earn 10 coins for each vote! Build your streak by voting daily! Submit your own questions!")

    await interaction.response.send_message(embed=embed)

# Run the bot
if __name__ == '__main__':
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found in .env file")
    else:
        bot.run(TOKEN)
