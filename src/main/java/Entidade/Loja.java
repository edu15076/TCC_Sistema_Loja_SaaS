package Entidade;

import java.io.Serializable;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.MapsId;
import jakarta.persistence.OneToOne;
import jakarta.persistence.Table;

@Entity
@Table(name = "loja")
public class Loja implements Serializable {
    @Id
    private long idContratante;
    private String nome_da_empresa;
    private byte[] logo;
    
    @OneToOne
    @MapsId 
    @JoinColumn(name = "id_contratante")
    private Contratante contratante;

    public long getIdContratante() {
        return idContratante;
    }

    public void setIdContratante(long idContratante) {
        this.idContratante = idContratante;
    }

    public String getNome() {
        return nome_da_empresa;
    }

    public void setNome(String nome_da_empresa) {
        this.nome_da_empresa = nome_da_empresa;
    }

    public byte[] getLogo() {
        return logo;
    }

    public void setLogo(byte[] logo) {
        this.logo = logo;
    }

    public Contratante getContratante() {
        return contratante;
    }

    public void setContratante(Contratante contratante) {
        this.contratante = contratante;
    }
}
