using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Text.RegularExpressions;
using LearningSystem.Utility;

namespace LearningSystem.ChangeLog
{
    public partial class ChangeLogFrm : Form
    {
        public ChangeLogFrm(String changelog)
        {
            InitializeComponent();
            this.richTextBox1.Text = changelog;

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
            this.StartPosition = FormStartPosition.Manual;
            this.Location = new Point(workingArea.Width / 2, workingArea.Height / 2);
        }

        private void ChangeLogFrm_Load(object sender, EventArgs e)
        {
            ChangeLogFormat();
            
        }

        private void ChangeLogFormat()
        {
            this.richTextBox1.ReadOnly = true;
            this.richTextBox1.BackColor = System.Drawing.Color.White;
            this.richTextBox1.BorderStyle = System.Windows.Forms.BorderStyle.None;

            string[] lines = this.richTextBox1.Lines;

            for (int i = 0; i < lines.Length; i++)
            {
                if (Regex.IsMatch(lines[i], Regexes.REGEXDATE))
                {
                    richTextBox1.Select(richTextBox1.GetFirstCharIndexFromLine(i), this.richTextBox1.Lines[i].Length);
                    richTextBox1.SelectionFont = new Font(richTextBox1.Font.FontFamily, 15F, FontStyle.Bold);
                    richTextBox1.SelectionColor = Color.Red;
                    
                }
            }
            richTextBox1.Select(richTextBox1.Text.Length - 1, 0);
            richTextBox1.SelectionLength = 0;
        }
    }
}
