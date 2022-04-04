using System;
using System.Net;
using System.Text;

namespace LearningSystem
{
    public partial class LoginFrm : Form
    {
        public LoginFrm()
        {
            InitializeComponent();
        }

        private void Setup_Screen()
        {


            // Screen adjust
            Rectangle workingArea = Screen.PrimaryScreen.WorkingArea;


            Width = Width >= workingArea.Width ? workingArea.Width : Width;
            Height = Height >= workingArea.Height ? workingArea.Height : Height;

            this.Location = new Point()
            {
                X = Math.Max(workingArea.X, workingArea.X + (workingArea.Width - this.Width) / 2),
                Y = Math.Max(workingArea.Y, workingArea.Y + (workingArea.Height - this.Height) / 2)
            };


            // Position
            this.StartPosition = FormStartPosition.CenterScreen;


        }

        private void Properties_Init()
        {
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.BackColor = Color.White;
            this.password_textbox.UseSystemPasswordChar = true;
        }

        
        private void Form1_Load(object sender, EventArgs e)
        {
            Setup_Screen();
            Properties_Init();
        }

        private void showpass_checkbox_CheckedChanged(object sender, EventArgs e)
        {
            this.password_textbox.UseSystemPasswordChar = this.showpass_checkbox.Checked ? false : true;
        }

        private void button2_Click(object sender, EventArgs e)
        {
            string changelog = new Utility.ChangelogReader().
                Changelog(@"https://raw.githubusercontent.com/trungducbu1337/online_testing_system/main/Changelog.log");
            ChangeLog.ChangeLogFrm changeLogFrm = new ChangeLog.ChangeLogFrm(changelog);
            changeLogFrm.ShowDialog();
        }
    }
}