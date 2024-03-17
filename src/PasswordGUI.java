

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.IOException;

public class PasswordGUI extends JFrame {
    public String[] files;
    private final Object lock = new Object();
    private JTextField passwordField;
    private JButton setPasswordButton;
    private JButton submitButton;
    private String storedPassword;

    public PasswordGUI() {
        setTitle("Password Management");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(350, 200);
        setLayout(new FlowLayout());

        createSetPasswordGUI();
    }

    private void createSetPasswordGUI() {
        JLabel setPasswordLabel = new JLabel("Set Password:");
        add(setPasswordLabel);

        passwordField = new JPasswordField(20);
        add(passwordField);

        setPasswordButton = new JButton("Set Password");
        setPasswordButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                storedPassword = passwordField.getText();
                System.out.println("Password Set: " + storedPassword);
                passwordField.setText("");
                passwordField.setEnabled(true);
                setPasswordButton.setEnabled(false);
                Waiting();
            }
        });
        add(setPasswordButton);
    }
    private void Waiting() {
        SwingWorker<Void, Void> backgroundWorker = new SwingWorker<Void, Void>() {
            @Override
            protected Void doInBackground() throws Exception {
                // Simulate background tasks for 3 seconds
                System.out.println("Please Wait....");
                Thread.sleep(3000);
                System.out.println("Ready..");
                return null;
            }

            @Override
            protected void done() {
                // After background tasks are done, enable password entry
                System.out.println("Allowing password entry now");
                getContentPane().removeAll();
                createEnterPasswordGUI();
                revalidate();
                repaint();
            }
        };
        backgroundWorker.execute();
    }
    private void createEnterPasswordGUI() {
        JLabel enterPasswordLabel = new JLabel("Enter Password:");
        add(enterPasswordLabel);

        passwordField = new JPasswordField(20);
        add(passwordField);

        submitButton = new JButton("Submit Password");
        submitButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                String enteredPassword = passwordField.getText();
                if (storedPassword != null && enteredPassword.equals(storedPassword)) {
                    System.out.println("Password Correct! Access Granted.");
                    dispose(); // Close the GUI window
                    synchronized (lock) {
                        lock.notify(); // Notify the waiting thread
                    }
                } else {
                    System.out.println("Incorrect Password! Access Denied.");
                }
                passwordField.setText("");
            }
        });
        add(submitButton);
    }
    public void waitForSubmit() {
        synchronized (lock) {
            try {
                lock.wait(); // Wait until the button is clicked
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    public void launchGUI() {
        SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                setVisible(true);
            }
        });
    }
    public static void PasswordLock() throws IOException {
        BlacklistGUI blacklist = new BlacklistGUI();
        blacklist.launchGUI();
        blacklist.waitForSubmit();
        String[] files= Applications.AbsoluteFinder().toArray(new String[0]);
        Applications.LockApplications(files);
        BlacklistGUI.lockWebsites();
        PasswordGUI passwordGUI = new PasswordGUI();
        passwordGUI.launchGUI();
        passwordGUI.waitForSubmit();
        Applications.UnlockApplications(files);
        BlacklistGUI.unlockWebsites();
    }

    public static void main(String[] args) throws IOException {
        PasswordLock();
    }
}
